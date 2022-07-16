import uvicorn

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=3176, log_level="info", reload=True, access_log=False)
 
