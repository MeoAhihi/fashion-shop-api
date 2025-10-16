# fashion-shop-api

## Getting Started

Follow these steps to set up and run the project locally.

### 1. Clone the repository

```bash
git clone <repository-url>
cd fashion-shop-api
```

### 2. Set up the environment

- Ensure you have [Python 3.8+](https://www.python.org/downloads/) installed.
- Install [pip](https://pip.pypa.io/en/stable/installation/) if necessary.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

- Copy the sample environment file and set your configuration:

```bash
cp .env.example .env
```
- Edit the `.env` file to include your MongoDB connection string and other settings as needed.

Example variables:
```
MONGO_URI=<your-mongodb-uri>
MONGO_DB=fashion_shop
JWT_SECRET=your_secret_key
JWT_TTL_MINUTES=60
```

### 5. Start the server

```bash
flask --app api run
```

- The API will be available at `http://localhost:5000/`

### 6. Using the API

- See `auth.http` and `user.http` for example API requests you can try with tools like [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) or [Postman](https://www.postman.com/).
