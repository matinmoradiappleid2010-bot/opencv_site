import streamlit as st
import numpy as np
import cv2
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model
from email.message import EmailMessage
import smtplib
import os
hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("please login first")
    st.switch_page('pages/loginorsignup.py')
    st.stop()
st.title("MATIN Site")
st.write("Age , Gender , Emotions")
@st.cache_resource
def load_models():
    model=cv2.FaceDetectorYN.create("models/face_detection_yunet_2022mar.onnx","",(320,320),score_threshold=0.9,nms_threshold=0.3,top_k=5000)
    ehsas_model=load_model('models/emotion_detection.h5')
    net_age=cv2.dnn.readNetFromCaffe('models/age_deploy.prototxt','models/age_net.caffemodel')
    net_gender=cv2.dnn.readNetFromCaffe('models/gender_deploy.prototxt','models/gender_net.caffemodel')
    return model,ehsas_model,net_age,net_gender
model,ehsas_model,net_age,net_gender=load_models()
######HQ
def HQ(c):
    ker=np.array([[0,0,0],[0,2,0],[0,0,0]])
    ker2=1/9*np.array([[1,1,1],[1,1,1],[1,1,1]])
    p=ker-ker2
    k5=cv2.filter2D(c,-1,p)
    k5_copy=k5
    return k5_copy
######ehsasat
def ehsasat(w):
    if w is None:
        st.error('plase try again later')
    else:
        h,w_=w.shape[:2]
        model.setInputSize((w_,h))
        res=model.detect(w)
        if res[1] is None:
            st.error('no face in photo')
            return
        face=res[1][0]
        x,y,wf,hf=face[:4].astype(int)
        face_crop=w[y:y+hf,x:x+wf]
        ehsas_img=cv2.cvtColor(face_crop,cv2.COLOR_BGR2GRAY)
        ehsas_img=cv2.resize(ehsas_img,(48,48))
        ehsas_img=ehsas_img/255.0
        ehsas_img=np.reshape(ehsas_img,(1,48,48,1))
        ehsasList=['Angry','Disgust','Fear','Happy','Sad','Surprise','Neutral']
        preds=ehsas_model.predict(ehsas_img)
        emotion=ehsasList[np.argmax(preds)]
        cv2.putText(w,str(emotion),(300,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
        w=cv2.cvtColor(w,cv2.COLOR_BGR2RGB)
        w_copy=w.copy()
        return w_copy
######age and gender
def age_gender(flip3):
    if flip3 is None:
        st.error('plase try again later')
    else:
        MODEL_MEAN_VALUES=(78.4263377603,87.7689143744,114.895847746)
        ageList=['(0-2)','(4-6)','(8-12)','(15-20)','(25-32)','(38-43)','(48-53)','(60-100)']
        genderList=['Male','Female']
        h,w,_=flip3.shape
        model.setInputSize((w,h))
        res=model.detect(flip3)    
        if res[1] is not None:
            for i in res[1]:
                c=i[:-1].astype(np.int32)
                img_crop=flip3[max(0,c[1]-15):min(h,c[1]+c[3]+15),max(0,c[0]-15):min(w,c[0]+c[2]+15)]
                blob_age=cv2.dnn.blobFromImage(img_crop,1.0,(227, 227),MODEL_MEAN_VALUES,swapRB=False)
                blob_gender=cv2.dnn.blobFromImage(img_crop,1.0,(227, 227),MODEL_MEAN_VALUES,swapRB=False)
                net_age.setInput(blob_age)
                net_gender.setInput(blob_gender)
                pre_age=net_age.forward()
                pre_gender=net_gender.forward()
                d=ageList[np.argmax(pre_age[0])]
                n=genderList[np.argmax(pre_gender[0])]
                label33=f"{n},{d}"
                cv2.putText(flip3,str(label33),(10,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
                flip3p=cv2.cvtColor(flip3,cv2.COLOR_BGR2RGB)
                flip3_copy=flip3p
                return flip3_copy
#####email
def send_email(to_email,img):
    password=os.getenv("EMAIL_PASSWORD")
    if password is None:
        st.error('email not password')
    else:
        msg=EmailMessage()
        msg['Subject']='Your Image'
        msg['From']="matinmoradi.appleid2010@gmail.com"
        msg['To']=to_email
        msg.set_content('Here is your processed image 😊')
        _,img_encoded=cv2.imencode('.jpg',img)
        img_bytes=img_encoded.tobytes()
        msg.add_attachment(img_bytes,maintype='image',subtype='jpeg',filename='you_photo.jpg')
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("matinmoradi.appleid2010@gmail.com",password)
            server.send_message(msg)
########set
if "camera_on" not in st.session_state:
    st.session_state["camera_on"]=False
if "uploud_on" not in st.session_state:
    st.session_state["uploud_on"]=False
if "whats" not in st.session_state:
    st.session_state["whats"]=False
########button camera
if st.button('Camera',type='primary'):
    st.session_state['camera_on']=False
    st.session_state['uploud_on']=False
    st.session_state["camera_on"]=True
if st.session_state["camera_on"]:
    img=st.camera_input('take a picture')
    if img is not None:
        img2=img.getvalue()
        img3=np.frombuffer(img2,np.uint8)
        frame=cv2.imdecode(img3,cv2.IMREAD_COLOR)
        img_bgr=cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
        how=st.radio('whats:',['HQ photo','Age and gender','Emotions'])
        if st.button('Done',type='primary'):
            st.session_state["whats"]=True
        if st.session_state['whats']:
            if how=='Emotions':
                result=ehsasat(img_bgr)
                if result is not None:
                    st.image(result,channels='BGR')
                    email=st.text_input('Write your email')
                    if st.button("Send Email"):
                        if email:
                            send_email(email,result)
                            st.success("Email sent ✅")
                            st.session_state['whats']=False
                        else:
                            st.warning("Enter email")
                    
            if how=='Age and gender':
                result=age_gender(img_bgr)
                if result is not None:
                    st.image(result,channels='BGR')
                    email=st.text_input('Write your email')
                    if st.button("Send Email"):
                        if email:
                            send_email(email,result)
                            st.success("Email sent ✅")
                            st.session_state['whats']=False
                        else:
                            st.warning("Enter email")
                    
            if how=='HQ photo':
                result=HQ(frame)
                if result is not None:
                    st.image(result,channels='BGR')
                    email=st.text_input('Write your email')
                    if st.button("Send Email"):
                        if email:
                            send_email(email,result)
                            st.success("Email sent ✅")
                            st.session_state['whats']=False
                        else:
                            st.warning("Enter email")
                    
########button uploud
if st.button('Upload',type='primary'):
    st.session_state['uploud_on']=False
    st.session_state['camera_on']=False
    st.session_state["uploud_on"]=True
if st.session_state['uploud_on']:
    uploaded_file=st.file_uploader("Choose an image")
    if uploaded_file is not None:
        image=Image.open(uploaded_file)
        st.image(image,caption="Uploaded Image",use_column_width=True)
        image_np=np.array(image)
        img_bgr=cv2.cvtColor(image_np,cv2.COLOR_RGB2BGR)
        how=st.radio('whats:',['HQ photo','Age and gender','Emotions'])
        if st.button('Done',type='primary'):
            st.session_state["whats"]=True
        if st.session_state['whats']:
            if how=='Emotions':
                result=ehsasat(img_bgr)
                if result is not None:
                    st.image(result,channels='RGB')
                    img_result=cv2.cvtColor(result,cv2.COLOR_BGR2RGB)
                    email=st.text_input('Write your email')
                    if st.button("Send Email"):
                        if email:
                            send_email(email,img_result)
                            st.success("Email sent ✅")
                            st.session_state['whats']=False
                        else:
                            st.warning("Enter email")
                    
            if how=='Age and gender':
                result=age_gender(img_bgr)
                if result is not None:
                    st.image(result,channels='RGB')
                    img_result=cv2.cvtColor(result,cv2.COLOR_BGR2RGB)
                    email=st.text_input('Write your email')
                    if st.button("Send Email"):
                        if email:
                            send_email(email,img_result)
                            st.success("Email sent ✅")
                            st.session_state['whats']=False
                        else:
                            st.warning("Enter email")
                    
            if how=='HQ photo':
                result=HQ(image_np)
                if result is not None:
                    st.image(result,channels='RGB')
                    img_result=cv2.cvtColor(result,cv2.COLOR_BGR2RGB)
                    email=st.text_input('Write your email')
                    if st.button("Send Email"):
                        if email:
                            send_email(email,img_result)
                            st.success("Email sent ✅")
                            st.session_state['whats']=False
                        else:
                            st.warning("Enter email")
                    