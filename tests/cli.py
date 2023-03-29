'''
This script simplifies running the playwright and pyunit tests.
'''
import os
import signal
import time
import subprocess
import typer
from dotenv import dotenv_values

CONFIG = dotenv_values(".env")
if 'BROWSER' not in CONFIG:
    CONFIG['BROWSER'] = 'firefox'

CMD = {
    'STREAMLIT_RUN': 'streamlit run main.py --client.showErrorDetails false --server.port 9000 --server.headless true',
    'PLAYWRIGHT': f"pytest ./tests/feature/*.py --browser {CONFIG['BROWSER']}",
    'PYUNIT': 'unittest discover -s tests.unit -p "*.py"',
    'REPORT': 'poetry run coverage report && poetry run coverage html'
}

app = typer.Typer()

@app.command()
def run(test: str = 'all'):
    '''
    Main run command interface for cli
    '''
    if test == 'all':
        print('Running PyUnit tests:')
        poetry_pyunit_cmd =f"poetry run coverage run --source src -m {CMD['PYUNIT']}"
        subprocess.run(poetry_pyunit_cmd, check=False, shell=True)

        print('Launching Streamlit server')
        streamlit_cmd =f"poetry run coverage run --append --source src -m {CMD['STREAMLIT_RUN']}"
        # pylint: disable-next=subprocess-popen-preexec-fn
        streamlit_process = subprocess.Popen(streamlit_cmd, stderr=subprocess.STDOUT, shell=True, preexec_fn=os.setsid)

        time.sleep(4)
        try:
            subprocess.run(f"poetry run {CMD['PLAYWRIGHT']}", stderr=subprocess.STDOUT, check=True, shell=True)
        except subprocess.CalledProcessError as _exc:
            # Do no harm
            pass

        os.killpg(os.getpgid(streamlit_process.pid), signal.SIGKILL)

        print('COVERAGE REPORT:')
        subprocess.run(CMD['REPORT'], check= False, shell=True)
    elif test == 'playwright':
        print('Launching Streamlit server')
        streamlit_cmd =f"poetry run {CMD['STREAMLIT_RUN']}"
        # pylint: disable-next=consider-using-with
        streamlit_process = subprocess.Popen(streamlit_cmd, stderr=subprocess.STDOUT, shell=True)

        time.sleep(4)
        try:
            subprocess.run(f"poetry run {CMD['PLAYWRIGHT']}", stderr=subprocess.STDOUT, check=True, shell=True)
        except subprocess.CalledProcessError as _exec:
            # Do no harm
            pass

        os.killpg(os.getpgid(streamlit_process.pid), signal.SIGKILL)
    elif test == 'pyunit':
        print('Running PyUnit tests:')
        poetry_pyunit_cmd =f"poetry run python -m {CMD['PYUNIT']}"
        subprocess.run(poetry_pyunit_cmd, stderr=subprocess.STDOUT, check=True, shell=True)
    else:
        typer.echo('Invalid option, please pick from the following: [all/playwright/pyunit]')

if __name__ == "__main__":
    app(prog_name='cli')
