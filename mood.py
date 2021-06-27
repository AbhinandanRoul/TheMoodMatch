import streamlit as st
import mysql.connector, time

# -------Database Info------------------
host='localhost'
database='mood'
user='root'
password='1234'
# --------------------------------------

st.title('Mood Match')
st.subheader('Need someone to talk to! MoodMatch finds a person with a similar mood to you.')
add_selectbox = st.sidebar.selectbox(
    "NAVIGATION",  # Title of sidebar
    (
        "SignUp", 'Login')
    # List of all options in sidebar
)
if add_selectbox== 'Login':

    # -------------------------------Insert a new Entry----------------------------------------------------
    def Insert_Entry(email, happiness, sadness, fear, disgust, anger, surprise, moodindex):
        mydb=mysql.connector.connect(host=host, database=database, user=user, password=password)
        my_cursor=mydb.cursor()
        sql_insert= "INSERT INTO moodscores (email, happiness, sadness, fear, disgust, anger, surprise, moodindex)" \
                    " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        insert_tuple=(email, happiness, sadness, fear, disgust, anger, surprise, moodindex)
        result=my_cursor.execute(sql_insert,insert_tuple)
        mydb.commit()
        Sort_Table()
    # ---------------------------------------------------------------------------------------------------

    # --------------------------Update an entry-----------------------------------------------------------
    def Update_Entry (email, happiness, sadness, fear, disgust, anger, surprise, moodindex):
        mydb = mysql.connector.connect(host=host, database=database, user=user, password=password)
        my_cursor = mydb.cursor()
        sql_update = "update moodscores set happiness={happiness}, sadness={sadness}, fear={fear}," \
                     " disgust={disgust}, anger={anger}, surprise={surprise}, " \
                     "moodindex={moodindex} where email=\"{email}\"".format( happiness=happiness,
                        sadness=sadness, fear=fear, disgust=disgust, anger=anger,
                        surprise=surprise, moodindex=moodindex,email=email)
        my_cursor.execute(sql_update)
        mydb.commit()
        Sort_Table()
    # --------------------------------------------------------------------------------------------------

    # ---------------------To check whether an entry is already present-------------------------
    def Is_Entry_Present(email):
        mydb = mysql.connector.connect(host=host, database=database, user=user, password=password)
        my_cursor = mydb.cursor()
        sql_find="select * from moodscores where email=\"{email}\"".format(email=email)
        k=my_cursor.execute(sql_find)
        myresult = my_cursor.fetchall() # Fetch all columns for any entry
        try:
            myresult[0][0] # Check if there are any values, if entry exists
            k=True
        except:
            k=False
        return k
    # ------------------------------------------------------------------------------------------

    # ------------------------------Password Verification------------------------------------------
    def password_verify(email,user_password):
        mydb = mysql.connector.connect(host=host, database=database, user=user, password=password)
        my_cursor = mydb.cursor()
        sql_verify="select password from userlist where email=\"{email}\"".format(email=email)
        my_cursor.execute(sql_verify)
        res=my_cursor.fetchone()[0]
        if res==user_password:
            return True
        else:
            return False
    # ---------------------------------------------------------------------------------------------

    def Find_Name(email):
        mydb = mysql.connector.connect(host=host, database=database, user=user, password=password)
        my_cursor = mydb.cursor()
        sql_verify = "select username from userlist where email=\"{email}\"".format(email=email)
        my_cursor.execute(sql_verify)
        res = my_cursor.fetchone()[0]
        return res


    email_list=[]; moodindex_list=[];
    def Sort_Table():
        mydb = mysql.connector.connect(host=host, database=database, user=user, password=password)
        my_cursor = mydb.cursor()
        sql_ops="select * from moodscores order by moodindex ASC"
        my_cursor.execute(sql_ops)
        res=my_cursor.fetchall()
        for x in res:
            email_list.append(x[0])
            moodindex_list.append(x[7])
        mydb.commit()

    email=st.text_input('Enter your email')
    user_password = st.text_input('Enter password',type='password')

    def button():
        k=st.button('Login')
        return k

    def Login(email, user_password):
        if password_verify(email, user_password):
            return True
        else:
            return False

    def Main_Ops():

            username=Find_Name(email)
            st.subheader('Hi {}!'.format(username))

            st.header('Select your emotional levels')
            """
            Use the slider to increase and decrease levels for Happiness, Sadness, Fear, Disgust, Anger, Surprise
            """
            e1 = st.slider("Happiness",min_value=0.0, max_value=10.0,step=0.5,help='Select happiness level')
            e2 = st.slider("Sadness",min_value=0.0, max_value=10.0, step=0.5)
            e3 = st.slider("Fear",min_value=0.0, max_value=10.0, step=0.5)
            e4 = st.slider("Disgust",min_value=0.0, max_value=10.0, step=0.5)
            e5 = st.slider("Anger",min_value=0.0, max_value=10.0, step=0.5)
            e6 = st.slider("Surprise",min_value=0.0, max_value=10.0, step=0.5)

            weight_dict={'Happiness':7,'Sadness':-4,
                         'Fear':-2,'Disgust':-5,
                         'Anger':-7,'Surprise':8} # Mentioning Weights for each emotion

            emotion_code_dict={'Happiness':e1,'Sadness':e2,
                         'Fear':e3,'Disgust':e4,
                         'Anger':e5,'Surprise':e6} # Access code for each emotion

            val_sum=0
            for key in weight_dict:
                val_sum+=weight_dict.get(key)*emotion_code_dict.get(key) # Sum of product of emotion levels and their weights
            mood_index=round((val_sum/6.0),2)
            st.subheader('Your Mood Index: {}'.format(mood_index))


            if st.button('Submit'): # On submit do the following
                if Is_Entry_Present(email):
                    Update_Entry(email, e1, e2, e3, e4, e5, e6, mood_index)
                else:
                    Insert_Entry(email, e1, e2, e3, e4, e5, e6, mood_index)
                st.success('Submitted')

                my_mood_index = moodindex_list.index(mood_index)  # Index of my mood in sorted list
                if (my_mood_index != len(moodindex_list) - 1):
                    mymatch_mood_index = moodindex_list[my_mood_index + 1];  # Extract a mood index succeeding my mood
                    mymatch_index = my_mood_index + 1  # Find the next mood index
                else:
                    mymatch_mood_index = moodindex_list[my_mood_index - 1];  # Extract a mood index succeeding my mood
                    mymatch_index = my_mood_index - 1  # Find the next mood index

                mymatch_email = email_list[mymatch_index]  # find email of the next/prev mood index
                # st.write(mymatch_mood_index, mymatch_email) # To write matched persons email and mood index
                st.balloons()
                """
                ## You've got a match
                """
                st.subheader(Find_Name(mymatch_email))
                st.write('Contact at:',mymatch_email)
    try:
        if(Login(email, user_password)): # IF login is successful, run the main ops function
            Main_Ops()
    except:
        st.warning('Enter email and password')

if add_selectbox=='SignUp':
    st.header('Create an account')
    name = st.text_input('Enter your name')
    email = st.text_input('Enter your email')
    user_password = st.text_input('Enter your password', type='password')
    password_conf = st.text_input('Enter password again',type='password')
    if (user_password != password_conf):
        st.warning('Password Mismatch')


    # -------------------------------Insert a new Entry----------------------------------------------------
    def Insert_Entry_in_Reg(email, username, user_password):
        mydb = mysql.connector.connect(host=host, database=database, user=user, password=password)
        my_cursor = mydb.cursor()
        sql_insert = "INSERT INTO userlist (email, username, password) VALUES (%s,%s,%s)"
        insert_tuple = (email, username, user_password)
        result = my_cursor.execute(sql_insert, insert_tuple)
        mydb.commit()


    # ---------------------------------------------------------------------------------------------------

    if st.button('Register') and user_password == password_conf:
        Insert_Entry_in_Reg(email, name, user_password)
        st.success('Registration success')
