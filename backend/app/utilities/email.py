"""
Email Utility Module

Handles all email sending functionality using Resend.
This module provides a clean interface for sending various types of emails.
"""

import os
import resend
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Resend
resend.api_key = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def send_email(to: str, subject: str, html: str) -> bool:
    """
    Send an email using Resend.
    
    Args:
        to: Recipient email address
        subject: Email subject line
        html: HTML content of the email
    
    Returns:
        True if sent successfully, False otherwise
    """
    if not to:
        print("ERROR: No recipient email provided")
        return False
    
    if not resend.api_key:
        print("ERROR: RESEND_API_KEY is not set")
        return False
        
    try:
        params = {
            "from": FROM_EMAIL,
            "to": [to],
            "subject": subject,
            "html": html,
        }
        
        print(f"Sending email to: {to}, subject: {subject}")
        response = resend.Emails.send(params)
        print(f"Email sent successfully: {response}")
        return True
        
    except Exception as e:
        print(f"Failed to send email to {to}: {type(e).__name__}: {e}")
        return False


def send_password_reset_email(to: str, reset_token: str) -> bool:
    """
    Send a password reset email with a link containing the reset token.
    
    Args:
        to: Recipient email address
        reset_token: The secure token for password reset
    
    Returns:
        True if sent successfully, False otherwise
    """
    reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}"
    
    subject = "Reset Your Password - Recipe Manager"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 28px;">🍴 Recipe Manager</h1>
        </div>
        
        <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333; margin-top: 0;">Reset Your Password</h2>
            
            <p>We received a request to reset your password. Click the button below to create a new password:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; 
                          padding: 14px 30px; 
                          text-decoration: none; 
                          border-radius: 6px; 
                          font-weight: bold;
                          display: inline-block;">
                    Reset Password
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                This link will expire in <strong>1 hour</strong> for security reasons.
            </p>
            
            <p style="color: #666; font-size: 14px;">
                If you didn't request a password reset, you can safely ignore this email. 
                Your password will remain unchanged.
            </p>
            
            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
            
            <p style="color: #999; font-size: 12px; margin-bottom: 0;">
                If the button doesn't work, copy and paste this link into your browser:<br>
                <a href="{reset_url}" style="color: #667eea; word-break: break-all;">{reset_url}</a>
            </p>
        </div>
        
        <p style="color: #999; font-size: 12px; text-align: center; margin-top: 20px;">
            © 2026 Recipe Manager. All rights reserved.
        </p>
    </body>
    </html>
    """
    
    return send_email(to, subject, html)


def send_welcome_email(to: str, name: str) -> bool:
    """
    Send a welcome email to newly registered users.
    
    Args:
        to: Recipient email address
        name: User's name
    
    Returns:
        True if sent successfully, False otherwise
    """
    subject = "Welcome to Recipe Manager! 🍴"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 28px;">🍴 Recipe Manager</h1>
        </div>
        
        <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333; margin-top: 0;">Welcome, {name}! 👋</h2>
            
            <p>Thank you for joining Recipe Manager. We're excited to have you!</p>
            
            <p>With Recipe Manager, you can:</p>
            <ul style="color: #555;">
                <li>Browse restaurants and their menus</li>
                <li>Manage your restaurant's recipes</li>
                <li>Connect with food lovers</li>
            </ul>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{FRONTEND_URL}/login" 
                   style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; 
                          padding: 14px 30px; 
                          text-decoration: none; 
                          border-radius: 6px; 
                          font-weight: bold;
                          display: inline-block;">
                    Get Started
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                If you have any questions, feel free to reach out to our support team.
            </p>
        </div>
        
        <p style="color: #999; font-size: 12px; text-align: center; margin-top: 20px;">
            © 2026 Recipe Manager. All rights reserved.
        </p>
    </body>
    </html>
    """
    
    return send_email(to, subject, html)


def send_verification_email(to: str, verification_token: str, name: str) -> bool:
    """
    Send an email verification link to a newly registered user.
    
    Args:
        to: Recipient email address
        verification_token: The secure token for email verification
        name: User's first name for personalization
    
    Returns:
        True if sent successfully, False otherwise
    """
    verify_url = f"{FRONTEND_URL}/verify-email?token={verification_token}"
    
    subject = "Verify Your Email - Recipe Manager"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 28px;">🍴 Recipe Manager</h1>
        </div>
        
        <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333; margin-top: 0;">Welcome, {name}! 👋</h2>
            
            <p>Thanks for signing up for Recipe Manager. Please verify your email address by clicking the button below:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verify_url}" 
                   style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; 
                          padding: 14px 30px; 
                          text-decoration: none; 
                          border-radius: 6px; 
                          font-weight: bold;
                          display: inline-block;">
                    Verify Email Address
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                This link will expire in <strong>24 hours</strong>.
            </p>
            
            <p style="color: #666; font-size: 14px;">
                If you didn't create an account with Recipe Manager, you can safely ignore this email.
            </p>
            
            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
            
            <p style="color: #999; font-size: 12px; margin-bottom: 0;">
                If the button doesn't work, copy and paste this link into your browser:<br>
                <a href="{verify_url}" style="color: #667eea; word-break: break-all;">{verify_url}</a>
            </p>
        </div>
        
        <p style="color: #999; font-size: 12px; text-align: center; margin-top: 20px;">
            © 2026 Recipe Manager. All rights reserved.
        </p>
    </body>
    </html>
    """
    
    return send_email(to, subject, html)
