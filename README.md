# Banking System API

This is a simple banking system API built with FastAPI and SQLAlchemy. It allows you to manage accounts and transactions.

## Features

- Create, read, update, and delete accounts
- Deposit, withdraw, and transfer funds between accounts
- Create and view transactions

## Requirements

- Python 3.7+
- FastAPI
- SQLAlchemy
- Pydantic

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/BenWorkSpace/banking_system.git
    cd banking_system
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Running the Application

1. Start the FastAPI server:
    ```sh
    uvicorn main:app --reload
    ```

2. Open your browser and navigate to `http://127.0.0.1:8000` to see the welcome message.

3. The API documentation is available at `http://127.0.0.1:8000/docs`.

## API Endpoints

### Accounts

- `GET /api/v1/accounts`: Get all accounts
- `POST /api/v1/accounts`: Create a new account
- `GET /api/v1/accounts/{account_id}`: Get a specific account by ID
- `PUT /api/v1/accounts/{account_id}`: Update an account by ID
- `DELETE /api/v1/accounts/{account_id}`: Delete an account by ID

### Transactions

- `GET /api/v1/accounts/{account_id}/transactions`: Get all transactions for an account
- `POST /api/v1/accounts/{account_id}/transactions`: Create a new transaction for an account
- `DELETE /api/v1/accounts/{account_id}/transactions/{transaction_id}`: Delete a transaction by ID

### Funds Management

- `POST /api/v1/accounts/{account_id}/deposit`: Deposit funds into an account
- `POST /api/v1/accounts/{account_id}/withdraw`: Withdraw funds from an account
- `POST /api/v1/accounts/{account_id}/transfer`: Transfer funds between accounts

## Error Handling

The API uses HTTP status codes to indicate the success or failure of an API request. Common status codes include:

- `200 OK`: The request was successful.
- `201 Created`: The resource was successfully created.
- `400 Bad Request`: The request was invalid or cannot be served.
- `404 Not Found`: The requested resource could not be found.
- `500 Internal Server Error`: An error occurred on the server.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
