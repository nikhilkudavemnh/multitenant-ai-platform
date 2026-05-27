
def get_final_response(data, status_code: int, elapsed_time: float) -> dict:
    return {
        "statusCode": status_code,
        "data": data,
        "executionTime": elapsed_time,
    }

