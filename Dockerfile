FROM public.ecr.aws/lambda/python:3.12

# Copy requirements and install dependencies
COPY lambda/requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy application code
COPY src/stock_agent ${LAMBDA_TASK_ROOT}/stock_agent
COPY lambda/handler.py ${LAMBDA_TASK_ROOT}/

# Set the handler
CMD [ "handler.handler" ]
