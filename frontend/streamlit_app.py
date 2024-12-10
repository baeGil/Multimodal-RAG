# python -m streamlit run streamlit_app.py
from redis_client import redis_client as redis_conn
import streamlit as st
import json, requests, uuid, httpx
import time

API_URL = "http://127.0.0.1:8000"

# Hàm quản lý session
def get_all_sessions():
    sessions = redis_conn.get("all_sessions")
    return json.loads(sessions) if sessions else []

def save_all_sessions(sessions):
    redis_conn.set("all_sessions", json.dumps(sessions))

def create_new_session():
    url = f"{API_URL}/session/create/"
    session_id = str(uuid.uuid4())
    sessions = get_all_sessions()
    session_name = f"Session {len(sessions) + 1}"
    session_data = json.dumps({"session_name": session_name, "session_id": session_id})
    response = requests.post(url,data=session_data)
    if response.status_code != 200:
        st.error("Error!!!")
    sessions.append({"id": session_id, "name": session_name})
    # save to redis
    save_all_sessions(sessions)
    return session_id, session_name

def get_chat_history(session_id):
    history = redis_conn.get(f"chat_history:{session_id}")
    return json.loads(history) if history else []

def save_chat_history(session_id, history):
    success = redis_conn.set(f"chat_history:{session_id}", json.dumps(history))
    if not success:
        st.error("Failed to save chat history to Redis")

def get_uploaded_files(session_id):
    files = redis_conn.get(f"uploaded_files:{session_id}")
    return json.loads(files) if files else []

def save_uploaded_files(session_id, files):
    redis_conn.set(f"uploaded_files:{session_id}", json.dumps(files))

def save_uploaded_file(session_id, session_name, file):
    url = f"{API_URL}/file/upload/"
    # Tạo dữ liệu session
    session_data = json.dumps({"session_id": session_id, "session_name": session_name})
    # Định nghĩa tệp tin
    files = {'file': file}
    # Gửi yêu cầu POST, sử dụng `json` cho session_data và `files` cho tệp tin
    response = requests.post(url, data={"session": session_data}, files=files)
    # Kiểm tra kết quả phản hồi
    if response.status_code == 200:
        st.success("File uploaded an processed successfully.")
    else:
        st.error("Error when uploading file !!")
    # Lấy đường dẫn tệp tin từ phản hồi
    file_path = response.text
    print(file_path)
    return file_path

def ask_question(session_id, session_name, question):
    url = f"{API_URL}/qa/"
    question_data = json.dumps({
        'session_id': session_id,
        'session_name': session_name,
        'question': question
    })
    try:
        response = requests.post(url, data=question_data)  
        if response.status_code == 200:
            return eval(response.text) # Evaluate the given source in the context of globals and locals then return result
        else:
            return "Error when making a question !! "
    except httpx.RequestError as e:
        return f"Connection error: {e}"

# Sidebar
with st.sidebar:
    st.title("Sessions")
    if st.button("Create New Session"):
        session_id, session_name = create_new_session()
        st.session_state.current_session = {"id": session_id, "name": session_name}
        st.rerun()

    # Hiển thị danh sách các session
    sessions = get_all_sessions()
    for session in sessions:
        if "current_session" in st.session_state and session["id"] == st.session_state.current_session["id"]:
            st.markdown(f"**:blue[{session['name']}]**")  # Hiển thị session hiện tại
        else:
            if st.button(session["name"], key=session["id"]):
                # Chuyển session
                st.session_state.current_session = session
                st.rerun()

# Giao diện chờ nếu chưa có session
if "current_session" not in st.session_state or not get_all_sessions():
    st.title("Welcome to the RAG Assistant!")
    st.write("Choose or create a new session to start your conversation !!!")
else:
    # Giao diện chính
    current_session = st.session_state.current_session
    st.title(f"Session: {current_session['name']}")

    # Load dữ liệu của session hiện tại
    # Kiểm tra và lấy dữ liệu từ Redis hoặc khởi tạo mới
    uploaded_files = get_uploaded_files(current_session["id"])

    # Upload file với key động liên kết session ID
    unique_file_uploader_key = f"file_uploader_{current_session['id']}"
    uploaded_file = st.file_uploader(
        "A file must be uploaded before asking , the file must contains less or equal than 15 tables/ images!!",
        type=["txt", "pdf"], key=unique_file_uploader_key
    )
    # Kiểm tra nếu file đã được tải lên trước đó
    if uploaded_file and uploaded_file.name not in [file["name"] for file in uploaded_files]:
        file_path = save_uploaded_file(current_session["id"], current_session["name"], uploaded_file)  # call the API
        if file_path:
            uploaded_files.append({"name": uploaded_file.name, "path": file_path})
            save_uploaded_files(current_session["id"], uploaded_files)  # save to redis
            st.success(f"File '{uploaded_file.name}' uploaded successfully!")
            st.write("You may need to reload the page!")
    else:
        if uploaded_file:
            st.info(f"File '{uploaded_file.name}' has already been uploaded!")

    # Hiển thị danh sách tệp của session hiện tại
    st.subheader("Uploaded Files:")
    for file in uploaded_files:
        st.write(f"- {file['name']} ({file['path']})")

    # st.session_state.chat_history = history
    history = get_chat_history(current_session["id"])
    if "history" not in st.session_state:
        st.session_state.history = []
    
    st.subheader("Chat with the Assistant")
    messages = st.container(height=600, border=True)
    with messages:
        for chat in history:
            st.chat_message(chat["role"]).write(chat["content"])
            
    # React to user input
    if prompt := st.chat_input("What is up?"):
        # Render the question
        messages.chat_message("user").write(prompt)
        # Get the answer from API
        response = ask_question(current_session["id"], current_session["name"], prompt)
        # Append to session_state to watch if any changes happen
        new_question = {"role": "user", "content": prompt}
        st.session_state.history.append(new_question)
        history.append(new_question)
        if response: 
            new_answer = {"role": "assistant", "content": response}
            # Append to session_state again if any changes happen 
            st.session_state.history.append(new_answer)
            
            # Render the answer word-by-word effect !!!
            full_ans = "" 
            holder = messages.empty()
            for word in response.split():
                full_ans += word + " "
                time.sleep(0.15)
                holder.chat_message("assistant").write(full_ans + "▌", unsafe_allow_html=True) # allow HTML to render as it was instead of raw string
            holder.chat_message("assistant").write(full_ans)
        
        # Finally save to redis
        history.append(new_answer)
        save_chat_history(current_session["id"], history)