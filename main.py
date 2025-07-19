from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField, IntegerField
from openai import OpenAI
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()


openai_api_key = os.getenv("API_KEY")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')



client = OpenAI(api_key=openai_api_key)

class ScheduleForm(FlaskForm):
    age = IntegerField('Age', validators=[DataRequired()])
    time_frame = StringField('Time_Frame', validators=[DataRequired()])
    first = StringField('First', validators=[DataRequired()])
    second = StringField('Second', validators=[DataRequired()])
    third = StringField('Third', validators=[DataRequired()])
    fourth = StringField('Fourth')
    fifth = StringField('Fifth')
    Generate = SubmitField('Generate Schedule')

input = {
    "role": "system",
    "content": """
    - You are a personal schedule planner who provides a schedule in the time interval provided based on the users age given
    - Along with the generated schedule, the schedule must also incorporate any of the user's listed activities
    - This should provide the user with a full daily schedule that meets their needs
    - Make sure that you are polite, but also critical on any advice you could give them to maintain a good schedule
    - make sure the schedule is actually organized in an optimal way rather than the events done all at the beginning
"""
}

chat_log = [input]

@app.route("/", methods=["GET", "POST"])
def index():
    form = ScheduleForm()
    if form.validate_on_submit():
        user = f"My activities are: {form.first.data}, {form.second.data}, {form.third.data}, {form.fourth.data}, and {form.fifth.data}. " \
                       f"My available time frame is {form.time_frame.data}. " \
                       f"My age is {form.age.data}."
        
        chat_log = [input, {"role": "user", "content": user}]
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=chat_log
        )
        AI_response = response.choices[0].message.content

        return render_template("bot.html", user_input = user, reply=AI_response)
    return render_template("schedule-bot.html", form=form)

@app.route("/bot", methods=['GET', 'POST'])
def bot():
    if request.method == "POST":
        first = request.form.get("first")
        second = request.form.get("second")
        third = request.form.get("third")
        fourth = request.form.get("fourth")
        fifth = request.form.get("fifth")
        age = request.form.get("age")
        time_frame = request.form.get("time_frame")
        user_input = f"My activities are: {first}, {second}, {third}, {fourth}, and {fifth}. My available time frame is {time_frame} and my age is {age}."


        chat_log.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model='gpt-4o',
            messages=chat_log
        )

        reply = response.choices[0].message.content
        chat_log.append({"role": "assistant", "content": reply})
        return render_template('bot.html', user_input = user_input, reply = reply)
    return render_template("bot.html")

if __name__ == "__main__":
    app.run(debug=True)
