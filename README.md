# ✈️ AI Flight Booking Agent

An AI-powered Flight Booking Assistant built using **FastAPI**, **LangGraph**, **LangChain**, and **Groq LLM**. The application allows users to search flights, retrieve flight details, book tickets, and cancel bookings using natural language.

---

# Features

- 🔍 Natural language flight search
- 🤖 AI-powered conversation using Groq LLM
- 🛫 Flight recommendations
- 🎫 Flight booking
- ❌ Booking cancellation
- 🧠 Conversation memory using LangGraph MemorySaver
- ⚡ FastAPI REST API
- 📂 JSON-based mock flight database
- 🔧 Tool-based Agent Architecture

---

# Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI |
| AI Framework | LangGraph |
| LLM Framework | LangChain |
| LLM | Groq |
| Memory | LangGraph MemorySaver |
| Data Storage | JSON (Mock Data) |
| API Validation | Pydantic |


---

# Architecture

```
                    +----------------------+
                    |      User            |
                    +----------+-----------+
                               |
                               |
                               ▼
                    +----------------------+
                    |      FastAPI         |
                    |    /chat Endpoint    |
                    +----------+-----------+
                               |
                               ▼
                  +-------------------------+
                  |     Flight Agent        |
                  |    (LangGraph Graph)    |
                  +-----------+-------------+
                              |
          +-------------------+------------------+
          |                                      |
          ▼                                      ▼
+-----------------------+             +------------------------+
|     Agent Node        |             |      Tool Node         |
|  Groq LLM + Prompt    |             | Executes Tool Calls    |
+-----------+-----------+             +-----------+------------+
            |                                     |
            |                                     |
            ▼                                     ▼
        Tool Decision                    Flight Tools
                                              |
       +--------------------------------------+----------------------------------+
       |                  |                     |                               |
       ▼                  ▼                     ▼                               ▼
Search Flights    Flight Details        Book Flight                  Cancel Booking
       |                  |                     |                               |
       +------------------+---------------------+-------------------------------+
                                      |
                                      ▼
                              JSON Flight Records
                              Booking Memory Store
```

---

# Agent Workflow

```
User Query
     │
     ▼
FastAPI Endpoint
     │
     ▼
LangGraph Agent
     │
     ▼
LLM understands intent
     │
     ▼
Needs Tool?
     │
 ┌───┴─────────────┐
 │                 │
Yes               No
 │                 │
 ▼                 ▼
Execute Tool   Generate Response
 │
 ▼
Return Tool Result
 │
 ▼
LLM Formats Response
 │
 ▼
Return to User
```

---

# Available Tools

## Search Flights

Searches available flights based on:

- Source
- Destination
- Date
- Airline
- Minimum Price
- Maximum Price

Example:

```
Find flights from Bangalore to Delhi tomorrow.
```

---

## Flight Details

Returns complete information of a flight.

Example

```
Show details for AI101
```

---

## Book Flight

Books a flight.

Required information

- Flight ID
- Passenger Name
- Passenger Email

Example

```
Book AI101 for John Doe.
Email: john@gmail.com
```

---

## Cancel Booking

Cancels an existing booking.

Example

```
Cancel booking 5f4ab123
```

---

# REST API

## Home

```
GET /
```

Response

```json
{
  "message": "AI Flight Booking Agent Running",
  "version": "2.0"
}
```

---

## Chat

```
POST /chat
```

Request

```json
{
    "message":"Find flights from Bangalore to Delhi on 2026-07-10",
    "thread_id":"user1"
}
```

Response

```json
{
    "response":"I found two available flights...",
    "thread_id":"user1"
}
```

---

## Health

```
GET /health
```

Example Response

```json
{
    "status":"healthy",
    "flights_available":25,
    "total_bookings":3
}
```

---

# Conversation Memory

The application maintains conversation state using **LangGraph MemorySaver**.

Example:

```
User:
Find flights to Delhi.

Assistant:
Here are available flights.

User:
Book the cheapest one.

Assistant:
Booking confirmed.
```

The assistant remembers previous context within the same `thread_id`.

---

# Flight Search Flow

```
User
 │
 ▼
Search Request
 │
 ▼
LLM
 │
 ▼
search_flights()
 │
 ▼
records.json
 │
 ▼
Matching Flights
 │
 ▼
LLM Summary
 │
 ▼
User
```

---

# Booking Flow

```
User
 │
 ▼
Book Flight
 │
 ▼
book_flight()
 │
 ▼
Validate Flight
 │
 ▼
Check Seat Availability
 │
 ▼
Generate Booking ID
 │
 ▼
Update Seat Count
 │
 ▼
Store Booking
 │
 ▼
Confirmation
```

---

# Cancellation Flow

```
User
 │
 ▼
Cancel Booking
 │
 ▼
Locate Booking
 │
 ▼
Update Status
 │
 ▼
Restore Seat
 │
 ▼
Confirmation
```

---

# Running the Application

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## Start Server

```bash
python main.py
```

or

```bash
uvicorn main:app --reload --port 9000
```

---

# Example Conversations

### Search

```
Find flights from Bangalore to Delhi on 2026-07-10.
```

---

### Cheapest Flight

```
Find the cheapest flight from Bangalore to Delhi.
```

---

### Flight Details

```
Show details for AI101.
```

---

### Booking

```
Book AI101 for John Doe.
Email is john@gmail.com.
```

---

### Cancellation

```
Cancel booking 7c82ab12.
```

---

# License

This project is intended for learning and demonstration purposes. Replace the mock JSON dataset with a real airline API and persistent database for production deployments.