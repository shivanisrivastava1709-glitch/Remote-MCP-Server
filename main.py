from fastmcp import FastMCP
import os
import sqlite3
import random

mcp = FastMCP(name = "Demo Server")

@mcp.tool 
def add_numbers(a:int, b:int)->int:
    return a+b

if __name__ == "__main__":
    mcp.run(transport="http", host ="0.0.0.0", port= 8000)