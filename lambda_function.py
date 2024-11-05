import json
import boto3
from uuid import uuid4
import logging

logging.basicConfig(level=logging.INFO)

def lambda_handler(event, context):
    client = boto3.client('bedrock-agent-runtime')
    session_id = str(uuid4())
    
    # Lấy query từ event
    q_ = event.get('query', '')
    

    if not q_:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Query parameter 'query' is missing."})
        }

    try:
        
        response = client.invoke_agent(
            agentAliasId="KZC4XWNCPU",
            agentId="HBMDMPAT6D",
            sessionId=session_id,
            inputText=q_
        )
        
        

        logging.info("Response from invoke_agent: %s", response)

        completion = response.get('completion', [])
        
        if not completion:
            logging.warning("No completion found in response.")
            return {
                'statusCode': 200,
                'body': json.dumps({"messages": ["No response from agent."]})
            }

        output_events = []
        for event in completion:
            chunk = event.get('chunk', 'No chunk content')
            logging.info("Chunk before processing: %s", chunk)  

            if isinstance(chunk, bytes):
                chunk = chunk.decode('utf-8') 
            
            output_events.append(chunk)
        return {
            'statusCode': 200,
            'body': json.dumps({"messages": [str(message) for message in output_events]})
        }

    except client.exceptions.AccessDeniedException as e:
        return handle_error(403, "Access Denied", e)
    except client.exceptions.InternalServerException as e:
        return handle_error(500, "Internal Server Error", e)
    except client.exceptions.ResourceNotFoundException as e:
        return handle_error(404, "Resource Not Found", e)
    except client.exceptions.ThrottlingException as e:
        return handle_error(429, "Throttling Exception", e)
    except Exception as e:
        return handle_error(500, "An unexpected error occurred", e)

def handle_error(status_code, message, exception):
    logging.error(f"{message}: {str(exception)}")
    return {
        'statusCode': status_code,
        'body': json.dumps({ "error": f"{message}: {str(exception)}" })
    }