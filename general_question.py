import os 
import random
import json
import re
from ibm_watsonx_ai.foundation_models import Model
import asyncio




def get_credentials():
  return {
      "url": "https://eu-de.ml.cloud.ibm.com",
      "apikey" : ''
  }
Project_id = ''
model_id = ''

parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 900,
    "repetition_penalty": 1.05
}

LLM_ALLaM =Model(
    model_id=model_id,
    params=parameters,
    credentials=get_credentials(),
    project_id=Project_id
)



general_stories = ['المدرسة', 'العائلة', 'الأصدقاء', 'الحديقة', 'المكتبة']


# Generate story prompt
def prompt_general_story(child_name, child_age, selected_story, characters = []):

    
    prompt = f'''
أنت تمثل دور المعلم "أريب" وهو معلم لطيف وظريف ويحب تعليم الأطفال العلوم عن طريق التجارب العلمية من خلال القصص الممتعة والذي سيكون عالمها هو البطل {child_name}

عنوان القصة: {selected_story} بطلها هو البطل{child_name} :

والآن، تخيل أن {child_name} بطل قصة مغامرات علمية، حيث تستمع إلى القصص المفيدة بطريقة ممتعة ومليئة بالمفاجآت. كل مرة تتعلم شيئًا جديدًا، تصبح مغامرتك أكثر إثارة!

 تذكر أن هدفنا هو أن نحكي قصص  ممتعة ومفيدة وكأنها لعبة مليئة بالتحديات والمغامرات يجب أن تكون القصة قصيرة وتتحدث عن ({selected_story}) بطلها هو {child_name}. هيا بنا ننطلق في هذه الرحلة الرائعة معًا!

 ملاحظة: الإجابة يجب أن تكون باللغة العربية فقط، ويجب أن تكون مناسبة لطفل في عمر {child_age}، خفيفة، ممتعة، قصيرة وسهلة الفهم.

وفي النهاية، سأروي لك قصة ممتعة عن ({selected_story}) تناسب عمرك لتبقى في ذاكرتك دائمًا!
'''
    return prompt


# Generate a yes/no question based on the generated story using Allam
def generate_yes_no_question_based_on_story(story):
    question_prompt = f"بناءً على هذه القصة: {story}\n، قم بإنشاء سؤال لطفل تكون إجابته بنعم أو لا وأذكر السؤال والجواب فقط كالتالي سؤال: جواب:"
    generated_question = LLM_ALLaM.generate_text(question_prompt)
    return generated_question


# Postprocess the Allam response on yes/no question
def post_processing_yes_no_question(text):
    match = re.search(r'سؤال:\s*(.*?)\n', text)
    if match:
        return match.group(1).strip().split('؟')[0].strip() + '?'
    
    else:
        return text.split('؟')[0].strip() + '?'


# Evaluate yes no question
async def eval_yes_no_question(child_name, child_age, story, child_response, question):

  
    evaluate_answer = f'''
     قيّم إجابة الطفل {child_name} بناءً على السؤال المعطى.
السؤال: {question}
إجابة الطفل: {child_response}
التقييم سيكون بالاعتماد على النص التالي : ({story})
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

    
    # evaluation_prompt = f'''"أنت تمثل شخصية المعلم "أريب المعلم اللبيب
    #  السؤال: {question}إجابة الطفل: {child_response} بالاعتماد على القصة : {story}
    #   بتقييم هذه الإجابة بشكل لطيف وقدم تغذية راجعة مفيدة وممتعة ومختصرة جدًا وقصيرة و مناسبة لطفل عمره {child_age}. قدم إجابة علمية صحيحة مع شرح بسيط.
    #  ملاحظة: تذكر أنك تتخاطب مع الطفل بشكل مباشر كن لطييفًا يجب عليك تشجيعه وشكره على إجابته، تذكر ان لاتشير للنص المعطى بشكل مباشر أبدًا ولا تقم بسؤال الطفل عن أي اسئلة إضافية
    # '''

    # response = LLM_ALLaM.generate_text(evaluation_prompt)

    # print(response)

    # return response
    
    # sentance = ''
    # for word in LLM_ALLaM.generate_text_stream(evaluation_prompt):
    #     sentance += word 
    #     if word == '\n':
    #         # if sentance == '\n':
    #         #     sentance = ''
    #         #     continue
    #         yield f"Evaluation: {sentance}\n"
    #         sentance = ''
    #         await asyncio.sleep(0.0000000001)


# Generate critical thinking response
def critical_thinking_general(child_name, child_age, story_text):

  
    problem_prompt = f"""
المطلوب منك:

استنادًا فقط على النص التالي، أنشئ موقفًا بسيطًا جدًا يشجع طفلًا بعمر {child_age} على التفكير الناقد، وذلك من خلال طرح سؤال يطلب منه توقع ما قد يحدث لاحقًا. النص: ({story_text})

التعليمات:
1. اكتب سؤالًا واضحًا ومباشرًا يعتمد بالكامل على النص المعطى ويبدو كأنك تخاطب طفلًا صغيرًا.
2. لا تضف أي معلومات أو تفاصيل غير موجودة في النص الأصلي.
3. تأكد أن الموقف قصير جدًا، واضح، ويطرح مرة واحدة فقط بدون أي تكرار للجمل.
4. يجب أن يكون الموقف مناسبًا لعمر الطفل ويعتمد فقط على النص المعطى.

المطلوب أن تكون الإجابة في اللغة العربية فقط.
"""

    # problem_prompt = f'''قم بالرجوع إلى هذه القصة فقط: {story_text}
    # وقم بإنشاء سؤال بسيط لموقف من القصة يتطلب تفكيرًا ناقدًا لطفل يبلغ من العمر {child_age}. '''
    generated_problem = LLM_ALLaM.generate_text(prompt=problem_prompt)

    #generated_problem = post_processing_yes_no_question(generated_problem)
    cleand = generated_problem.replace('"', '')
    cleand = cleand.replace('\n', '')
    if '؟' in cleand:    
        cleand = cleand.split('؟')[0]

    return cleand


# Evaluate critical thinking child response
async def eval_critical_thinking_general(child_name, child_age, stroy, generated_problem, child_answer):
    evaluation_prompt = f'''
     قيّم إجابة الطفل {child_name} بناءً على السؤال المعطى.

السؤال: {generated_problem}
إجابة الطفل: {child_answer}
النص المعطى:({stroy})
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
            #if sentance.endswith(':'):
            if bool(re.search(r'\s*:$', sentance)):
                sentance = ''
                continue

            sentance = re.sub(r'[^a-zA-Z0-9ء-ي:?؟\s]', '', sentance)

            yield f"Evaluation: {sentance}\n"
            sentance = ''
        await asyncio.sleep(0.0000000001)



async def run_interactive_story(child_name='Shahad', child_age=2, selected_story=2):
    
    selected_story_type = general_stories[selected_story-1]

    story_prompt = prompt_general_story(child_name, child_age, selected_story_type)

    generated_story = ""
    sentance = ""

    # Stream the story chunk by chunk
    for word in LLM_ALLaM.generate_text_stream(story_prompt):
        sentance += word 
        if word == '\n':
            if sentance == '\n':
                sentance = ''
                continue
            yield f"Story: {sentance}\n"
            generated_story += sentance
            sentance = ""
        await asyncio.sleep(0.0000000001)

    yield f"Full_Story: {generated_story}\n"

    # Generate a yes/no question based on the story
    question = generate_yes_no_question_based_on_story(generated_story)
    question = post_processing_yes_no_question(question)
    yield f"Question_yes_no: {question}\n"


if __name__ == "__main__":
     run_interactive_story()


