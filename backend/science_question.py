import random
import re
from ibm_watsonx_ai.foundation_models import Model
import asyncio
import boto3
import random
import io
import csv


def get_credentials():
  return {
      "url": "https://eu-de.ml.cloud.ibm.com",
      "apikey" : ''
  }
Project_id = ''
model_id = ''

parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 700,
    "repetition_penalty": 1.05,
    "temperature" : 0
}

LLM_ALLaM =Model(
    model_id=model_id,
    params=parameters,
    credentials=get_credentials(),
    project_id=Project_id
)


# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id='',
    aws_secret_access_key=''
)

# Function to load CSV data from S3
def load_csv_from_s3(bucket_name, key):
    response = s3.get_object(Bucket=bucket_name, Key=key)
    content = response['Body'].read().decode('utf-8')
    csv_data = []
    reader = csv.reader(io.StringIO(content))
    next(reader)  # Skip header row
    for row in reader:
        csv_data.append({"id": row[0], "question": row[1], "Arabic_Question": row[2],"retrieved_text": row[3], "Video": row[4]})
    return csv_data
# Load and shuffle CSV data based on subject choice
def get_subject_data(subject_choice):
    bucket_name = 'areeb-s3-test'
    if subject_choice == 6:  # Galaxy
        data = load_csv_from_s3(bucket_name, "galaxy_results.csv")
    elif subject_choice == 7:  # Chemistry
        data = load_csv_from_s3(bucket_name, "chemistry_results.csv")
    elif subject_choice == 8:  # Biology
        data = load_csv_from_s3(bucket_name, "biology_results.csv")
    else:
        return None

    return data  


# Generate story prompt
def prompt_science_story(child_name, child_age, question, retrieved_text):

    prompt = f'''
أنت تمثل دور المعلم "أريب" وهو معلم لطيف وظريف ويحب تعليم الأطفال العلوم عن طريق التجارب العلمية من خلال القصص الممتعة والذي سيكون عالمها هو البطل {child_name}

قم بشرح النص التالي : {retrieved_text} على شكل قصة علمية بسيطة بطلها هو العالم البطل  {child_name} :

قدم الشرح وكأنها قصة علمية بسيطةو لطيفة وظريفة وقصيرة موجهة لطفل يبلغ من العمر {child_age} لا تشير للنص المعطي بشكل مباشر وذات فائدة علمية كبيرة.

والآن، تخيل أن {child_name} بطل قصة مغامرات علمية، حيث تكتشف أسرار هذا العلم بطريقة ممتعة ومليئة بالمفاجآت. كل مرة تتعلم شيئًا جديدًا، تصبح مغامرتك أكثر إثارة!

 تذكر أن هدفنا هو أن نجعل العلوم ممتعة وكأنها لعبة مليئة بالتحديات والمغامرات يجب أن تكون القصة علمية بطلها هو {child_name}. هيا بنا ننطلق في هذه الرحلة الرائعة معًا!

 ملاحظة: الإجابة يجب أن تكون باللغة العربية فقط، ويجب أن تكون مناسبة لطفل في عمر {child_age}، خفيفة، ممتعة، قصيرة وسهلة الفهم.

وفي النهاية، سأروي لك قصة ممتعة عن هذا المفهوم تناسب عمرك لتبقى في ذاكرتك دائمًا!
'''


    return prompt 


# Evaluate first question child response
async def eval_first_question(child_name, child_age,question, retrieved_text, child_answer):

    evaluate_answer = f'''
     قيّم إجابة الطفل {child_name} بناءً على السؤال المعطى.
السؤال: {question}
إجابة الطفل: {child_answer}
النص المعطى:({retrieved_text})
قدم تقييمًا لطيفًا لإجابة الطفل.
استخدم أسلوبًا مشجعًا وودودًا يناسب طفلًا بعمر {child_age}.
اجعل التقييم قصيرًا جدًا وبسيطًا.
التغذية الراجعة:
قدم تصحيحًا علميًا بسيطًا ومناسبًا لعمر الطفل، إن لزم الأمر.
لا تُضف أي أسئلة جديدة ولا تذكر النص المعطى بشكل مباشر.
تذكر: تحدث إلى الطفل بطريقة تشجيعية ولطيفة، واشكره على إجابته.
لا تقل العبارات التالية : (إليك التقييم ، إليك التغذية الراجعة ، تقييم إجابة الطفل)وابدأ الرد بالتشجيع باسم الطفل
'''
    

    sentance = ''
    for word in LLM_ALLaM.generate_text_stream(evaluate_answer):
        sentance += word 
        if word == '\n':
            if sentance == '\n':
                sentance = ''
                continue
            if bool(re.search(r'\s*:$', sentance)):
                sentance = ''
                continue
            yield f"Evaluation: {sentance}\n"
            sentance = ''
        await asyncio.sleep(0.0000000001)
    


# Postprocess the Allam keywords result to match the exprected output
def post_process_keywords(result, child_name):
    words = []
    # Process each line in the text
    for line in result.splitlines():
        print(line)
        # Remove special characters and numbers
        cleaned_line = re.sub(r'[^أ-ي\s]', '', line)  # Arabic letters and whitespace
        # Append the cleaned word to the list if it's not empty
        if cleaned_line.strip():
            cleaned_line = cleaned_line.replace("كلمة", '').strip()
            if len(cleaned_line.split()) == 1:
                if cleaned_line == child_name:
                    print('child name is included in the keywords ...')
                    continue
                if cleaned_line == 'تجربة' or cleaned_line == 'أريب':
                    continue
                if cleaned_line in words:
                    continue
                words.append(cleaned_line.strip())

    if len(words) >= 3:
        return words[:3]
    
    else: 
        print('The words is empty..')

    return words


# Generate a keyword from stroy to improve the child's pronunciation
def generate_keywords_from_story(story, child_name):
    keywords_prompt = f""" 
    من هذا النص: {story}\n،  قم بإستخراج ١٥ كلمة علمية قد تساعد في تحسين نطق طفل يجب ان تكون الكلمات علمية، أذكر الكلمات فقط كما ذكرت بالقصة وضع كل كلمة بين - كالآتي كلمة١ - كملة٢ - كلمة٣، بدون اي وصف او كلام اضافي"""
    generated_keywords = LLM_ALLaM.generate_text(keywords_prompt)
    keywordsـoutputs = post_process_keywords(generated_keywords, child_name)
    return keywordsـoutputs


# Generate critical thinking response
def critical_thinking_science(child_name, child_age, story_text):
    problem_prompt = f"""
المطلوب منك:

اعتمد فقط على النص التالي لإنشاء تجربة علمية يناسب طفلًا بعمر {child_age} ويشجعه على التفكير الناقد من خلال سؤال الطفل أن يتوقع ما ذا سيحدث النص: ({story_text})
اكتب سؤالًا واضحًا ومباشرًا يستند بالكامل إلى النص المعطى يطلب من الطفل توثع ما قد سيحدث في الموقف العلمي، ويبدو كأنك تخاطب طفلًا صغيرًا

تنبيهات هامة:
لا تقدم أي معلومات أو تفاصيل غير موجودة في النص المعطى
يجب أن يستند الموقف إلى النص فقط، ويكون بسيطًا ومناسبًا لعمر الطفل
    """
    
    generated_problem = LLM_ALLaM.generate_text(prompt=problem_prompt)

    cleand = generated_problem.replace('\n', '')
    cleand = generated_problem.replace('"', '')

    cleand = re.sub(r'[^a-zA-Z0-9ء-ي:؟\s]', '', cleand)
    
    return cleand.split(':')[1]


# Evaluate critical thinking child response
async def eval_critical_thinking_science(child_name, child_age, generated_problem, child_answer):
    
    evaluation_prompt = f'''
     قيّم إجابة الطفل {child_name} بناءً على السؤال المعطى.
السؤال: {generated_problem}
إجابة الطفل: {child_answer}
قدم تقييمًا لطيفًا لإجابة الطفل.
استخدم أسلوبًا مشجعًا وودودًا يناسب طفلًا بعمر {child_age}.
اجعل التقييم قصيرًا جدًا وبسيطًا.
التغذية الراجعة:
قدم تصحيحًا علميًا بسيطًا ومناسبًا لعمر الطفل، إن لزم الأمر.
لا تُضف أي أسئلة جديدة ولا تذكر النص المعطى بشكل مباشر.
تذكر: تحدث إلى الطفل بطريقة تشجيعية ولطيفة، واشكره على إجابته.
لا تقل العبارات التالية : (إليك التقييم ، إليك التغذية الراجعة ، تقييم إجابة الطفل)وابدأ الرد بالتشجيع باسم الطفل
'''

    sentance = ''
    for word in LLM_ALLaM.generate_text_stream(evaluation_prompt):
        sentance += word 
        if word == '\n':
            if sentance == '\n':
                sentance = ''
                continue
            if bool(re.search(r'\s*:$', sentance)):
                sentance = ''
                continue
            yield f"Evaluation: {sentance}\n"
            sentance = ''
        await asyncio.sleep(0.0000000001)


async def run_interactive_science_stroy(child_name='Shahad', child_age=2, selected_story=2):

    # Load and shuffle the questions and retrieved text based on the chosen subject
    subject_data = get_subject_data(selected_story)
    # question = item = subject_data[0]
    # question = item["Arabic_Question"]
    # retrieved_text = item["retrieved_text"]
    # video = item["Video"]

    # print(question)




    while True:
        # Select a random item
        random_item = random.choice(subject_data)
        question = random_item["Arabic_Question"]
        retrieved_text = random_item["retrieved_text"]
        video = random_item["Video"]
        print('video')
        print(video)

        if video :
            break
    
    Question_prompt = (f"""
  أنت تمثل دور المعلم "أريب المعلم اللبيب" وهو معلم لطيف وظريف ويحب تعليم الأطفال العلوم، وستقوم مباشرة بالتحدث والترحيب بالطفل الذكي يبلغ من العمر  {child_age}. ، ثم ستطرح عليه السؤال هذا السؤال: {question}  بطريقة مناسبة لعمره وتنظر أن يجيبك على السؤال دون أن تشرح له الإجابة.

  الهدف هو إعادة صياغة السؤال بطريقة تناسب عمر لطفل وتوجيهه للطفل بشكل مباشر وكأنك تتحدث مع الطفل فقط وتنتظر منه أن يجيبك على السؤال. لا تقم بإضافة أي نص آخر ولا تقم بالإجابة على السؤال اتبع المثال التالي:

  المثال:  مرحبًا يا صغيري! أنا أريب، معلم العلوم الأريب. اليوم سنتعلم معًا عن المجرات والنجوم. هل تعرف يا ذكي كيف تختلف المجرات عن النجوم؟ إذا كنت تعرف الإجابة، أخبرني بها وسأكون سعيدًا لسماع رأيك الذكي. هيا بنا نتعلم معًا!

          """)
    
    print(Question_prompt)
    question_by_ALLaM = LLM_ALLaM.generate_text(prompt = Question_prompt)
    print(question_by_ALLaM)
    yield f"Question1: {question_by_ALLaM}\n"
    await asyncio.sleep(0.0000000001)

    # Generate the story prompt
    story_prompt = prompt_science_story(child_name, child_age, question, retrieved_text)

    generated_story = ''
    sentance = ''
    for word in LLM_ALLaM.generate_text_stream(story_prompt):
        sentance += word 
        if word == '\n':
            if sentance == '\n':
                sentance = ''
                continue
            yield f"Story: {sentance}\n"
            generated_story += sentance
            sentance = ''
        await asyncio.sleep(0.0000000001)

    yield f"Full_Story: {generated_story}\n"

    yield f"Retrieved_text: {retrieved_text}\n"

    print(video)

    yield f"Video: {video}\n"


if __name__ == "__main__":
     run_interactive_science_stroy()

