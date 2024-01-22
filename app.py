from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id
    

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:  
            return "there was an issue adding your ingredient"

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)
    
@app.route('/delete/<int:id>')   
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was an issue deleting your ingredient"


@app.route('/update/', methods=['GET', 'POST'])  
def update():
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue generating your recipe'
    else:
        tasks = Todo.query.all()
        lst = []
        for task in tasks:
            lst += [task.content]
        RecInfo = findBestRecipe(lst)
        RecipeName, Ingredients, Instructions = RecInfo[0], RecInfo[1], RecInfo[2]
        return render_template('update.html', RecipeName=RecipeName, Ingredients=Ingredients, Instructions=Instructions)
        

@app.route('/back/')
def back():
    return index()
    


#loading in data and cleaning
name = 'Food Ingredients and Recipe Dataset with Image Name Mapping.csv'
RecipeData = pd.read_csv(name).dropna()

#logic of getting a recipe from an input of recipes using database
def fs(myIngredients, ingredients):
    score = 0
    for ingredient in myIngredients:
        if ingredient in ingredients:
            score += 1
    return score

    
def findScore(myIngredients):
    return lambda x: fs(myIngredients, x)


def findBestRecipe(listOfIngredients):
    func = findScore(listOfIngredients)
    RecipeDataCopy = RecipeData.copy()
    RecipeDataCopy['Score'] = RecipeDataCopy["Cleaned_Ingredients"].apply(func)
    R = RecipeDataCopy.sort_values(by='Score', ascending=False)
    return [R.iloc[0]['Title'], R.iloc[0]['Ingredients'], R.iloc[0]['Instructions']]



if __name__ == "__main__":
    app.run(debug=True) 
