select 
                                w.id as word_id,
                                w.book,
                                w.lesson,
                                w.french, 
                                w.chinese, 
                                w.part_of_speech, 
                                w.part_of_speech_full_chinese  
                            from 
                                words as w LEFT JOIN exercise_words as wp
                                ON wp.word_id = w.id
                                AND wp.user_id = 2
                            where 
                                book=1 and lesson = 1
                                AND wp.word_id IS NULL
                                ORDER BY random()
                                LIMIT 10;