import streamlit as st
import time
import random
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from llm import contruct_prompt,get_llm_response
import json
load_dotenv()
from vector_database import vector_search_v1




def validate_user_input(system_prompt,question, user_input):
    response = get_llm_response(system_prompt, user_input, [])
    return json.loads(response)


def initialize_session_state():
    if 'state' not in st.session_state:
        st.session_state.state = 'initial'
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'search_result' not in st.session_state:
        st.session_state.search_result = None
    if 'futures' not in st.session_state:
        st.session_state.futures = None
    if 'futuresresult' not in st.session_state:
        st.session_state.futuresresult = False
    if 'search_start_time' not in st.session_state:
        st.session_state.search_start_time = None

def main():
    st.title("AI Receptionist")
    
    initialize_session_state()
    
    if st.session_state.state == 'initial':
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Emergency"):
                st.session_state.state = 'emergency'
                # st.session_state.conversation_history.append({"role": "assistant", "content": "Can you describe your emergency if possible in detail ?"})
                with st.spinner("Processing your emergency..."):
                    
                    st.session_state.conversation_history.append({"role": "assistant", "content": "Can you describe your emergency if possible in detail ?"})
                    # system_prompt = "You are an AI receptionist for a Doctor handling an emergency. Ask the patient to describe their emergency in detail."
                    # response = get_llm_response(system_prompt, "", st.session_state.conversation_history)
                    
                st.rerun()
        with col2:
            if st.button("Leave a Message"):
                st.session_state.state = 'message'

                with st.spinner("Processing your request..."):
                    st.session_state.conversation_history.append({"role": "assistant", "content": "Leave a message for the doctor"})
                    # system_prompt = "You are an AI receptionist for Doctor. A patient wants to leave a message. Ask them what message they'd like to leave for the Doctor."
                    # response = get_llm_response(system_prompt, "I want to leave a message.", st.session_state.conversation_history)
                    # st.session_state.conversation_history.append({"role": "assistant", "content": response})
                st.rerun()

    # Chat input
    if st.session_state.state in ['emergency', 'message', 'location', 'after_location', 'final','message_final']:
        for message in st.session_state.conversation_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        user_input = st.chat_input("Type your message here...")

        if user_input:
            # Add user message to conversation history
            st.session_state.conversation_history.append({"role": "user", "content": user_input})

            if st.session_state.state == 'emergency':
                with st.spinner("Processing your emergency..."):
                    with ThreadPoolExecutor() as executor:
                        validation_result_1 = validate_user_input("Just analyse if the user_input contains a valid symptom related to any health issue.Respond with a JSON object where 'response' is your analysis and 'validAnswer' is a boolean indicating if the answer is valid.\n Generate a JSON response in the following format without using the ```json block. Ensure the output is properly formatted as plain text JSON.","Which area are you located right now?", user_input)
                        if not validation_result_1['validAnswer']:
                            st.session_state.conversation_history.append({"role": "assistant", "content": f"I'm sorry, but I don’t understand that.Please just mention the Emergency the patient or anyone is facing.Other responses would be invalid."})
                            st.rerun()
                    
                        st.session_state.futures = executor.submit(vector_search_v1, user_input)
                        st.session_state.search_start_time = time.time()
                        
                        system_prompt = "I am checking what you should do immediately, meanwhile, can you tell me which area are you located right now?"
                        st.session_state.conversation_history.append({"role": "assistant", "content": system_prompt})
                        
                        if st.session_state.futures.done() and not st.session_state.futuresresult:
                            st.session_state.futuresresult = True
                            st.session_state.search_result = st.session_state.futures.result()
                            st.session_state.conversation_history.append({"role": "assistant", "content": f"Emergency instructions: {st.session_state.search_result}"})
                            system_prompt = "If you are done handling the emergency , can you tell me which area are you located right now?"
                            st.session_state.conversation_history.append({"role": "assistant", "content": system_prompt})
                    
                st.session_state.state = 'location'
                st.rerun()

            elif st.session_state.state == 'location':
                with st.spinner("Processing your location..."):
                    validation_result = validate_user_input("Just analyse if the user_input contains a location I mean , city , state or country.Respond with a JSON object where 'response' is your analysis and 'validAnswer' is a boolean indicating if the answer is valid.\n Generate a JSON response in the following format without using the ```json block. Ensure the output is properly formatted as plain text JSON.","Which area are you located right now?", user_input)
                    if not validation_result['validAnswer']:
                        st.session_state.conversation_history.append({"role": "assistant", "content": f"I'm sorry, but I didn't understand your location. Could you please provide a clear location?"})
                        st.rerun()
                    
                    if st.session_state.futures.done() and not st.session_state.futuresresult:
                        st.session_state.futuresresult = True
                        st.session_state.search_result = st.session_state.futures.result()
                        st.session_state.conversation_history.append({"role": "assistant", "content": f"Emergency instructions: {st.session_state.search_result}"})
                    
                    eta = random.randint(5, 20)
                    system_prompt = f"Doctor will be coming to your location immediately. Doctor's estimated arrival will be in {eta} minutes."
                    st.session_state.conversation_history.append({"role": "assistant", "content": system_prompt})
                
                st.session_state.state = 'after_location'
                st.rerun()

            elif st.session_state.state == 'after_location':
                print(user_input)
                with st.spinner("Processing your response..."):
                    response_0 = get_llm_response(system_prompt="Analyse the input where you will respond with 'late' or 'too long' strictly.You have to analyse that 'If the user says that the arrival will be too late' or any similar user_input but meaning is similar.Otherwise return 'other' strictly." , user_prompt=user_input ,conversation_history=[])
                    print(response_0)
                    if "late" in response_0.lower() or "too long" in response_0.lower():
                        if not st.session_state.futuresresult:
                            elapsed_time = time.time() - st.session_state.search_start_time
                            if elapsed_time < 15:
                                st.session_state.conversation_history.append({"role": "assistant", "content": "Please hold just a sec while I fetch the emergency instructions..."})
                                st.rerun()
                            else:
                                search_result = st.session_state.futures.result()
                                st.session_state.futuresresult = True
                        else:
                            search_result = st.session_state.search_result
                        
                        response = f"I understand that you are worried that Doctor will arrive too late. Meanwhile, we suggest that you follow these steps: {st.session_state.search_result}"
                        st.session_state.conversation_history.append({"role": "assistant", "content": response})

                st.session_state.conversation_history.append({"role": "assistant", "content": f"Thank you for using AI Receptionist. Is there anything else I can help you with? While you wait for the Doctor."})
                st.session_state.state = 'final'
                st.rerun()

            elif st.session_state.state == 'message':
                print("Inside the message state.")
                with st.spinner("Processing your message..."):
                    system_prompt = "You are an AI receptionist for a Doctor. A patient has left a message. Confirm that you've received the message and will pass it on to Doctor.Don't say anything other than that strictly."
                    response = get_llm_response(system_prompt, user_input, [])
                    print(response)
                    st.session_state.conversation_history.append({"role": "assistant", "content": response})
                
                st.session_state.state = 'message_final'
                st.rerun()
            
            elif st.session_state.state == 'message_final':
                response_4 =get_llm_response(system_prompt="Analyse the input where you will respond with 'emergency' or 'just_message' or 'other_rubbish' strictly.If the user_input conveys a meaning the its a emergency the just return emergency strictly or if user conveys he wants to add a message or wants to leave another message then return 'just_message' strictly.If its neither related to emergency or any message to doctor , then return other_rubbish strictly." , user_prompt=user_input ,conversation_history=[])
                print(response_4)
                if 'emergency' in response_4.lower():
                    st.session_state.state = 'emergency'
                    st.session_state.conversation_history.append({"role": "assistant", "content": "Can you describe your emergency if possible in detail ?"})
                    st.rerun()
                elif 'just_message' in response_4.lower():
                    st.session_state.conversation_history.append({"role": "assistant", "content": f"Sure please add whatever you wanted to add it to the previous message. "})  
                    st.session_state.state = 'message'
                    st.rerun()
                elif 'other_rubbish' in response_4.lower():
                    st.session_state.conversation_history.append({"role": "assistant", "content": f"I'm sorry, but I don’t understand that ? "})
                    st.rerun()
                    

            elif st.session_state.state == 'final':
                with st.spinner("Processing your message..."):
                    response_3 = get_llm_response(system_prompt="Analyse the input where you will respond with 'yes' or 'no' strictly.You have to analyse that 'If the user's input if user is satisfied or not' or any similar user_input but meaning is similar.Otherwise return 'other' strictly." , user_prompt=user_input ,conversation_history=[])
                                                    
                    if "yes" in response_3.lower():
                        st.session_state.state = 'initial'
                        st.session_state.conversation_history = []
                        st.session_state.search_result = None
                        st.session_state.futures = None
                        st.session_state.futuresresult = False
                        st.session_state.search_start_time = None
                        st.rerun()
                    elif "no" in response_3.lower():
                        st.session_state.conversation_history.append({"role": "assistant", "content": "Goodbye!"})
                        st.stop()
                    elif "other" in response_3.lower():
                        validation_result = validate_user_input("Analyse if user_input contains a feedback or not strictly.There is another case if you find where user_input is specifying that 'doctor arrival will be too late or when will the doctor arrive in that case add one more key 'doctor_arrival':True in the response json.Respond with a JSON object where 'response' is your analysis and 'validAnswer' is a boolean indicating if the answer is valid and 'doctor_arrival' as boolean if the user_input has the meaning containing doctor's arrival or any similar meaning user_input ,If sentence does not contain that then mark it as None. \n Generate a JSON response in the following format without using the ```json block. Ensure the output is properly formatted as plain text JSON.","", user_input)
                        print(validation_result)
                        if validation_result['doctor_arrival']:
                            st.session_state.conversation_history.append({"role": "assistant", "content":st.session_state.conversation_history[-2]['content'] })
                            st.rerun()
                        if not validation_result['validAnswer']:
                            st.session_state.conversation_history.append({"role": "assistant", "content": f"I'm sorry, but I didn't understand your response. Could you please provide with a feedback or you can restart the conversation by clicking on Reset conversation."})
                        st.rerun()

    # Reset button
    if st.button("Reset Conversation"):
        st.session_state.state = 'initial'
        st.session_state.conversation_history = []
        st.session_state.search_result = None
        st.session_state.futures = None
        st.session_state.futuresresult = False
        st.session_state.search_start_time = None
        st.rerun()

if __name__ == "__main__":
    main()