from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Temporary database (list)
books = []

@app.route('/')
def home():
    return render_template('index.html', books=books)

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        
        books.append({
            'title': title,
            'author': author,
            'available': True
        })
        
        return redirect('/')
    
    return render_template('add.html')

@app.route('/issue/<int:id>')
def issue_book(id):
    books[id]['available'] = False
    return redirect('/')

@app.route('/return/<int:id>')
def return_book(id):
    books[id]['available'] = True
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)