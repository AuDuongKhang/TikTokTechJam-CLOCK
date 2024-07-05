import streamlit as st
import streamlit_authenticator as stauth
import yaml
import time
from yaml.loader import SafeLoader
from text_to_sound import gen
from video_pose_prompt import process_video_pose
import os
from text_to_text import script_process
import text2video as vg  # Import the video generation module

def main():
    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Initialize authenticator
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    # Create a login widget
    name, authentication_status, username = authenticator.login()

    if authentication_status:
        authenticator.logout()

        st.title("TikTokTechJam-CLOCK")

        tab1, tab2, tab3 = st.tabs(
            ["Create Content/Video/Audio", "Create Video by Motion", "Create Script"])

        with tab1:
            st.header("Create Content, Video, and Audio")

            if 'content' not in st.session_state:
                content_text = st.text_area(
                    "Enter text to generate content", key='generate content')

                if st.button("Generate Content"):
                    st.session_state['content'] = "Generated content from: " + content_text
                    st.experimental_rerun()

            if 'content' in st.session_state:
                st.write(st.session_state['content'])

                if 'video' not in st.session_state and 'audio' not in st.session_state:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Back to Content Generation"):
                            del st.session_state['content']
                            st.experimental_rerun()

                    with col2:
                        st.subheader("Convert Content to Video")
                        prompt = st.text_input("Enter prompt for video generation", key='video_prompt')
                        negative_prompt = st.text_input("Enter negative prompt", key='negative_prompt')
                        video_duration = st.number_input("Enter video duration (seconds)", min_value=1, max_value=60, value=7)

                        if st.button("Generate Video"):
                            video_path = vg.generate_video(prompt, negative_prompt, video_duration)
                            st.session_state['video'] = video_path
                            st.experimental_rerun()

                    with col3:
                        if st.button("Convert Content to Audio"):
                            st.session_state['audio'] = "Generated audio from content: "
                            st.experimental_rerun()

                if 'video' in st.session_state:
                    st.write("Generated video from content:")
                    video_anime = vg.display_video(st.session_state['video'])
                    st.write(video_anime.to_html5_video(), unsafe_allow_html=True)
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("Back to Content Generation"):
                            del st.session_state['content']
                            del st.session_state['video']
                            st.experimental_rerun()

                    with col2:
                        if st.button("Back to Video or Audio Generation"):
                            del st.session_state['video']
                            st.experimental_rerun()

                if 'audio' in st.session_state:
                    st.write(st.session_state['audio'])
                    audio_file_path = 'out.wav'
                    prompt = st.session_state['content'].split(':')[1].strip()
                    gen(audio_file_path, prompt)
                    st.audio(audio_file_path, format='audio/wav')
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("Back to Content Generation"):
                            del st.session_state['content']
                            del st.session_state['audio']
                            st.experimental_rerun()

                    with col2:
                        if st.button("Back to Video or Audio Generation"):
                            del st.session_state['audio']
                            st.experimental_rerun()

        with tab2:
                st.header("Create Video by Motion")

                if 'motion_video' not in st.session_state:
                    motion_text = st.text_area("Enter text to generate motion video", "")
                    motion_video = st.file_uploader("Upload video for motion", type=["mp4", "mov", "avi"])
                    if motion_video is not None:
                        st.video(motion_video)  # Display the uploaded video
                        if st.button("Generate Motion Video"):
                            os.chdir('./FollowYourPose')
                            print(os.getcwd())

                            # Save the uploaded video to a temporary file
                            with open("temp_motion_video.mp4", "wb") as f:
                                f.write(motion_video.getbuffer())
                            
                            # Process the video and prompt
                            process_video_pose(motion_text, "temp_motion_video.mp4")
                            
                            st.session_state['motion_video'] = "Generated motion video from: " + motion_text
                            st.session_state['generated_video_path'] = "temp_motion_video.mp4"  # Path to the generated video
                            st.experimental_rerun()
                            os.chdir('..')
                            print(os.getcwd())
                    else:
                        st.error("Please upload a video for motion.")

                if 'motion_video' in st.session_state:
                    st.write(st.session_state['motion_video'])

                    # Display the generated video
                    if 'generated_video_path' in st.session_state:
                        st.video(st.session_state['generated_video_path'])

                    if 'motion_audio_video' not in st.session_state:
                        if st.button("Add Audio to Motion Video"):
                            st.session_state['motion_audio_video'] = "Generated motion video with audio"
                            st.experimental_rerun()
                        if st.button("Back to Motion Video Generation"):
                            del st.session_state['motion_video']
                            del st.session_state['generated_video_path']
                            st.experimental_rerun()

                    if 'motion_audio_video' in st.session_state:
                        st.write(st.session_state['motion_audio_video'])
                        if st.button("Back to Motion Video Generation"):
                            del st.session_state['motion_audio_video']
                            st.experimental_rerun()

        with tab3:
            st.header("Generate Script")
            st.markdown(script_process(st.session_state['script']))

            if 'script' not in st.session_state:
                script_text_2 = st.text_area(
                    "Enter text to generate script", key='generate script')

                if st.button("Generate Script"):
                    st.session_state['script'] = "Generated script from: " + \
                        script_text_2
                    st.experimental_rerun()

            if 'script' in st.session_state:
                st.write(st.session_state['script'])
                if st.button("Back to Script Generation"):
                    del st.session_state['script']
                    st.experimental_rerun()

    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')


if __name__ == "__main__":
    main()
