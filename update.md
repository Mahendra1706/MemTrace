1.in convo below there is un structure behaviour of read and write like they trigger any time and printed on terminal so we have to set up thing like it doesnt pront unneccesory thing like for read or write log only neccesory event log
2.insted of overwritten treat as failure we just log that here is the thing because overwritten happen with user intention also

3. sometime it store in the read and write both structure so we have to resolve this issue also 

==================================================
MemTrace — Live Chat
==================================================
  model: llama-3.3-70b-versatile   stm_capacity: 10
  Type your messages. Enter 'exit' to stop and see diagnosis.
============================================================

You: hello im mahendra
Agent: Hello Mahendra, it's nice to meet you.

  [LTM] [step=1] WRITE key=user_name value=mahendra meta={'importance': 0.9, 'source': 'llm_agent'}

You: i am study at LD college ahmedabad
Agent: I've noted that you study at LD college in Ahmedabad.

  [STM] [step=2] READ key=user_name value=None meta={'reason': 'llm_recall'}
  [LTM] [step=2] READ key=user_name value=mahendra meta={'reason': 'llm_recall'}
  [LTM] [step=3] WRITE key=college_name value=LD college meta={'importance': 0.85, 'source': 'llm_agent'}
  [LTM] [step=4] WRITE key=city_of_study value=ahmedabad meta={'importance': 0.85, 'source': 'llm_agent'}

You: i am currently learning Deep Learning
Agent: That's great, Mahendra! Deep Learning is a fascinating field.

  [STM] [step=5] READ key=user_name value=None meta={'reason': 'llm_recall'}
  [LTM] [step=5] READ key=user_name value=mahendra meta={'reason': 'llm_recall'}
  [STM] [step=6] READ key=college_name value=None meta={'reason': 'llm_recall'}
  [LTM] [step=6] READ key=college_name value=LD college meta={'reason': 'llm_recall'}
  [STM] [step=7] READ key=city_of_study value=None meta={'reason': 'llm_recall'}
  [LTM] [step=7] READ key=city_of_study value=ahmedabad meta={'reason': 'llm_recall'}
  [STM] [step=8] WRITE key=current_field_of_study value=Deep Learning meta={'importance': 0.5, 'source': 'llm_agent'}

You: the water in the bottle
Agent: I don't see any information about a bottle in our conversation so far, Mahendra.

  [STM] [step=9] READ key=current_field_of_study value=Deep Learning meta={'reason': 'llm_recall'}
  [STM] [step=10] READ key=user_name value=None meta={'reason': 'llm_recall'}
  [LTM] [step=10] READ key=user_name value=mahendra meta={'reason': 'llm_recall'}
  [STM] [step=11] READ key=college_name value=None meta={'reason': 'llm_recall'}
  [LTM] [step=11] READ key=college_name value=LD college meta={'reason': 'llm_recall'}
  [STM] [step=12] READ key=city_of_study value=None meta={'reason': 'llm_recall'}
  [LTM] [step=12] READ key=city_of_study value=ahmedabad meta={'reason': 'llm_recall'}

You: can you guess where am i study at
Agent: You study at LD college in Ahmedabad.

  [STM] [step=13] READ key=college_name value=None meta={'reason': 'llm_recall'}
  [LTM] [step=13] READ key=college_name value=LD college meta={'reason': 'llm_recall'}
  [STM] [step=14] READ key=city_of_study value=None meta={'reason': 'llm_recall'}
  [LTM] [step=14] READ key=city_of_study value=ahmedabad meta={'reason': 'llm_recall'}

You: the school has holiday today
Agent: The school has a holiday today.

  [STM] [step=15] READ key=school_holiday_status value=None meta={'reason': 'llm_recall'}
  [LTM] [step=15] READ key=school_holiday_status value=None meta={'reason': 'llm_recall'}
  [STM] [step=16] WRITE key=school_holiday_status value=today meta={'importance': 0.3, 'source': 'llm_agent'}

You: im actually study at the VGEC ahmedabad not LD college
Agent: I've updated your college name to VGEC, Ahmedabad.

  [STM] [step=17] READ key=college_name value=None meta={'reason': 'llm_recall'}
  [LTM] [step=17] READ key=college_name value=LD college meta={'reason': 'llm_recall'}
  [STM] [step=18] READ key=city_of_study value=None meta={'reason': 'llm_recall'}
  [LTM] [step=18] READ key=city_of_study value=ahmedabad meta={'reason': 'llm_recall'}
  [LTM] [step=19] UPDATE key=college_name value=VGEC meta={'old_value': 'LD college', 'old_importance': 0.85, 'importance': 0.85, 'source': 'llm_agent'}

You: can you able to write poetry for me
Agent: I'd be happy to try writing a poem for you, Mahendra. What kind of poem would you like me to write?

  [STM] [step=20] READ key=user_name value=None meta={'reason': 'llm_recall'}
  [LTM] [step=20] READ key=user_name value=mahendra meta={'reason': 'llm_recall'}
  [STM] [step=21] READ key=college_name value=None meta={'reason': 'llm_recall'}
  [LTM] [step=21] READ key=college_name value=VGEC meta={'reason': 'llm_recall'}

You: i like to here poet on one sided love
Agent: In the halls of VGEC, where hearts often roam, a secret love blossoms, yet remains unspoken, a one-sided flame that flickers, a heart that beats in vain, for mahendra, a love so true, yet destined to remain unheard, a poetic tale of unrequited love, in the city of ahmedabad, where love stories unfold.

  [STM] [step=22] READ key=user_name value=None meta={'reason': 'llm_recall'}
  [LTM] [step=22] READ key=user_name value=mahendra meta={'reason': 'llm_recall'}
  [STM] [step=23] READ key=college_name value=None meta={'reason': 'llm_recall'}
  [LTM] [step=23] READ key=college_name value=VGEC meta={'reason': 'llm_recall'}

You: dont use my name or college name just just create a small minimal poet
Agent: A heart beats in silence, a love so true, yet unspoken, a flame that flickers, a secret kept, in the shadows of the heart.

  [STM] [step=24] READ key=user_name value=None meta={'reason': 'llm_recall'}
  [LTM] [step=24] READ key=user_name value=mahendra meta={'reason': 'llm_recall'}
  [STM] [step=25] READ key=college_name value=None meta={'reason': 'llm_recall'}
  [LTM] [step=25] READ key=college_name value=VGEC meta={'reason': 'llm_recall'}

You: ^C
(interrupted)

==================================================
DIAGNOSIS
==================================================
  ✅  step=2  user_name = 'mahendra'
  ✅  step=5  user_name = 'mahendra'
  ✅  step=6  college_name = 'LD college'
  ✅  step=7  city_of_study = 'ahmedabad'
  ✅  step=9  current_field_of_study = 'Deep Learning'
  ✅  step=10  user_name = 'mahendra'
  ✅  step=11  college_name = 'LD college'
  ✅  step=12  city_of_study = 'ahmedabad'
  ✅  step=13  college_name = 'LD college'
  ✅  step=14  city_of_study = 'ahmedabad'
  ❌  step=15  school_holiday_status — memory_evicted
       Key 'school_holiday_status' was written at step 16
       READ at step 15 returned None
       Importance: 0.30 (normal)
       Likely evicted due to capacity overflow (indirect eviction)
  ✅  step=17  college_name = 'LD college'
  ✅  step=18  city_of_study = 'ahmedabad'
  ✅  step=20  user_name = 'mahendra'
  ❌  step=21  college_name — memory_overwritten
       Key 'college_name' was overwritten at step 19
       Old value: 'LD college' → New value: 'VGEC'
       Old importance: 0.85 (CRITICAL!)
       New importance: 0.85
       Recall attempted at step 21
  ✅  step=22  user_name = 'mahendra'
  ❌  step=23  college_name — memory_overwritten
       Key 'college_name' was overwritten at step 19
       Old value: 'LD college' → New value: 'VGEC'
       Old importance: 0.85 (CRITICAL!)
       New importance: 0.85
       Recall attempted at step 23
  ✅  step=24  user_name = 'mahendra'
  ❌  step=25  college_name — memory_overwritten
       Key 'college_name' was overwritten at step 19
       Old value: 'LD college' → New value: 'VGEC'
       Old importance: 0.85 (CRITICAL!)
       New importance: 0.85
       Recall attempted at step 25

   15 passed / 4 failed / 19 total reads

==================================================
DONE
==================================================