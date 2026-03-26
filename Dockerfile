FROM steffrhes/dev_env_jupyterlab:2025-08-20
RUN pip install jiwer==4.0.0
RUN pip install Levenshtein==0.27.1
RUN pip install openai==1.97.1
RUN pip install pandas==2.2.3
RUN pip install google-cloud-vision==3.10.2
RUN pip install google-generativeai==0.8.5
RUN pip install google-cloud-aiplatform==1.105.0
RUN pip install anthropic==0.59.0
RUN pip install requests==2.32.4
RUN pip install plotly==6.1.1
RUN pip install tabulate==0.9.0
RUN pip install kaleido==0.2.1
RUN pip install pillow==11.3.0

