import sys
from flask import Flask, render_template_string, redirect, url_for
from git import Repo

app = Flask(__name__)

@app.route('/')
def index():
    repo = Repo(app.config['REPO_PATH'])
    files = repo.git.ls_files().split('\n')

    commits = []
    for commit in repo.iter_commits():
        commits.append({
            'id': commit.hexsha,
            'message': commit.message,
            'author': commit.author.name,
            'date': commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')
        })

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Git Repository Viewer</title>
        <style>
        * {
            margin: 0;
            padding: 0;
        }

        body {
            font-family: "Courier New", Courier, monospace;
            font-weight: bold;
        }

        h1, h3{
            font-weight: normal;
        }

        .tabs{
            width: 600px;
            display: block;
            margin: 40px auto;
            position: relative;
        }

        .tabs .tab{
            float: left;
            display: block;
        }

        .tabs .tab>input[type="radio"] {
            position: absolute;
            top: -9999px;
            left: -9999px;
        }

        .tabs .tab>label {
            display: block;
            padding: 6px 21px;
            font-size: 12px;
            cursor: pointer;
            position: relative;
            color: #FFF;
            background: #4A83FD;
        }

        .tabs .content {
            z-index: 0;/* or display: none; */
            overflow: hidden;
            width: 600px;
            padding: 25px;
            position: absolute;
            top: 27px;
            left: 0;
            background: #fefefe;
            color: #000;
            opacity:0;
            transition: opacity 400ms ease-out;
        }

        .tabs>.tab>[id^="tab"]:checked + label {
            top: 0;
            background: #303030;
            color: #F5F5F5;
        }

        .tabs>.tab>[id^="tab"]:checked ~ [id^="tab-content"] {
            z-index: 1;/* or display: block; */
        
            opacity: 1;
            transition: opacity 400ms ease-out;
        }
        </style>
    </head>
    <body>
        <ul class="tabs">
            <li class="tab">
                <input type="radio" name="tabs" id="tab1" />
                <label for="tab1">Repository Contents</label>
                <div id="tab-content1" class="content">
                    <ul>
                    {% for file in files %}
                        <li><a href="{{ url_for('view_file', file_path=file) }}">{{ file }}</a></li>
                    {% endfor %}
                    </ul>
                </div>
            </li>

            <li class="tab">
                <input type="radio" name="tabs" id="tab2" />
                <label for="tab2">Commit History</label>
                <div id="tab-content2" class="content">
                    <ul>
                    {% for commit in commits %}
                        <li><a href="{{ url_for('view_commit', commit_id=commit.id) }}">{{ commit.message }}</a></li>
                    {% endfor %}
                    </ul>
                </div>
            </li>
        </ul>
    </body>
    </html>
    """

    return render_template_string(template, files=files, commits=commits)

@app.route('/file/<path:file_path>')
def view_file(file_path):
    repo = Repo(app.config['REPO_PATH'])
    try:
        file_content = repo.git.show('HEAD:{}'.format(file_path))
        return '<pre>{}</pre>'.format(file_content)
    except Exception as e:
        return str(e)

@app.route('/commit/<commit_id>')
def view_commit(commit_id):
    repo = Repo(app.config['REPO_PATH'])
    commit = repo.commit(commit_id)
    return f"<h1>Commit: {commit_id}</h1><p>{commit.message}</p><p>Author: {commit.author.name}</p><p>Date: {commit.committed_datetime}</p>"


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python app.py <repository_path>')
        sys.exit(1)
    app.config['REPO_PATH'] = sys.argv[1]
    app.run()

