from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import DateTime, create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, ValidationError

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./banking_system.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Account model
class AccountDB(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, default=0)
    owner = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = Column(DateTime, nullable=True)

# Transaction model
class TransactionDB(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, index=True)
    amount = Column(Float)
    type = Column(String)  # e.g., 'deposit', 'withdrawal', 'transfer'
    created_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)

Base.metadata.create_all(bind=engine)

# Pydantic model for request/response
class AccountCreate(BaseModel):
    owner: str
    balance: float = 0
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: datetime = None

class TransactionCreate(BaseModel):
    amount: float
    type: str  # e.g., 'deposit', 'withdrawal', 'transfer'
    created_at: datetime = datetime.now()
    deleted_at: datetime = None

class Account(AccountCreate):
    id: int
    balance: float
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime

    class Config:
        from_attributes = True  # This replaces orm_mode = True

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Allow all methods
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Custom exception handler for validation errors
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to the Banking System"}

@app.get("/api/v1/accounts")
def get_accounts(db: Session = Depends(get_db)):
    try:
        accounts = db.query(AccountDB).filter(AccountDB.deleted_at.is_(None)).all()
        return {"accounts": accounts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/accounts")
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    try:
        db_account = AccountDB(
            owner=account.owner,
            balance=account.balance,
            created_at=account.created_at,
            updated_at=account.updated_at,
            deleted_at=account.deleted_at,
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return {"message": "Account created successfully", "account": db_account}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/accounts/{account_id}")
def get_account(account_id: int, db: Session = Depends(get_db)):
    try:
        account = (
            db.query(AccountDB)
            .filter(AccountDB.id == account_id, AccountDB.deleted_at.is_(None))
            .first()
        )
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        return {"account": account}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/accounts/{account_id}")
def update_account(
    account_id: int, account: AccountCreate, db: Session = Depends(get_db)
):
    try:
        db_account = (
            db.query(AccountDB)
            .filter(AccountDB.id == account_id, AccountDB.deleted_at.is_(None))
            .first()
        )
        if db_account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        db_account.owner = account.owner
        db_account.balance = account.balance
        db.commit()
        db.refresh(db_account)
        return {"message": "Account updated successfully", "account": db_account}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    try:
        db_account = (
            db.query(AccountDB)
            .filter(AccountDB.id == account_id, AccountDB.deleted_at.is_(None))
            .first()
        )
        if db_account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        db.delete(db_account)
        db.commit()
        return {"message": "Account deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/accounts/{account_id}/deposit")
def deposit(account_id: int, amount: float, db: Session = Depends(get_db)):
    try:
        db_account = (
            db.query(AccountDB)
            .filter(AccountDB.id == account_id, AccountDB.deleted_at.is_(None))
            .first()
        )
        if db_account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        db_account.balance += amount
        db.commit()
        db.refresh(db_account)
        return {"message": "Deposit successful", "account": db_account}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/accounts/{account_id}/withdraw")
def withdraw(account_id: int, amount: float, db: Session = Depends(get_db)):
    try:
        db_account = (
            db.query(AccountDB)
            .filter(AccountDB.id == account_id, AccountDB.deleted_at.is_(None))
            .first()
        )
        if db_account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        if db_account.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        db_account.balance -= amount
        db.commit()
        db.refresh(db_account)
        return {"message": "Withdrawal successful", "account": db_account}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/accounts/{account_id}/transfer")
def transfer(
    account_id: int,
    target_account_id: int,
    amount: float,
    db: Session = Depends(get_db),
):
    try:
        source_account = (
            db.query(AccountDB)
            .filter(AccountDB.id == account_id, AccountDB.deleted_at.is_(None))
            .first()
        )
        target_account = (
            db.query(AccountDB)
            .filter(AccountDB.id == target_account_id, AccountDB.deleted_at.is_(None))
            .first()
        )
        if source_account is None or target_account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        if source_account.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        source_account.balance -= amount
        target_account.balance += amount
        db.commit()
        db.refresh(source_account)
        db.refresh(target_account)
        return {
            "message": "Transfer successful",
            "account": source_account,
            "target_account": target_account,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/accounts/{account_id}/transactions")
def get_transactions(account_id: int, db: Session = Depends(get_db)):
    try:
        transactions = (
            db.query(TransactionDB)
            .filter(
                TransactionDB.account_id == account_id, TransactionDB.deleted_at.is_(None)
            )
            .all()
        )
        return {"transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/accounts/{account_id}/transactions")
def create_transaction(
    account_id: int, transaction: TransactionCreate, db: Session = Depends(get_db)
):
    try:
        db_transaction = TransactionDB(
            account_id=account_id,
            amount=transaction.amount,
            type=transaction.type,
            created_at=transaction.created_at,
            deleted_at=transaction.deleted_at,
        )
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return {
            "message": "Transaction created successfully",
            "transaction": db_transaction,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/accounts/{account_id}/transactions/{transaction_id}")
def delete_transaction(
    account_id: int, transaction_id: int, db: Session = Depends(get_db)
):
    try:
        db_transaction = (
            db.query(TransactionDB)
            .filter(TransactionDB.id == transaction_id, TransactionDB.deleted_at.is_(None))
            .first()
        )
        if db_transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        db_transaction.deleted_at = datetime.now()
        db.commit()
        return {"message": "Transaction deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
