from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Request, Response

ForgotPasswordRouter = APIRouter(
    prefix = "/auth/forgot-password",
    tags=["Forgot Password"]
)