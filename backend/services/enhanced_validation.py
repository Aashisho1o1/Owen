"""
Enhanced Validation Service for DOG Writer
Provides detailed, user-friendly validation error messages for authentication
"""

import re
from typing import List, Dict, Any
from email_validator import validate_email, EmailNotValidError


class ValidationResult:
    """Result of validation with detailed error information"""
    def __init__(self):
        self.is_valid = True
        self.errors: List[Dict[str, Any]] = []
    
    def add_error(self, field: str, message: str, code: str = None):
        """Add a validation error"""
        self.is_valid = False
        self.errors.append({
            "field": field,
            "message": message,
            "code": code or f"{field}_invalid"
        })
    
    def get_error_messages(self) -> List[str]:
        """Get all error messages as a list"""
        return [error["message"] for error in self.errors]
    
    def get_field_errors(self) -> Dict[str, str]:
        """Get errors organized by field"""
        field_errors = {}
        for error in self.errors:
            field_errors[error["field"]] = error["message"]
        return field_errors


class AuthValidationService:
    """
    Comprehensive authentication validation service
    Provides detailed, specific error messages for better user experience
    """
    
    @staticmethod
    def validate_email(email: str) -> ValidationResult:
        """Validate email with detailed error messages"""
        result = ValidationResult()
        
        if not email or not email.strip():
            result.add_error("email", "Email address is required", "email_required")
            return result
        
        email = email.strip()
        
        # Basic format check
        if "@" not in email:
            result.add_error("email", "Email address must contain an '@' symbol", "email_missing_at")
            return result
        
        if "." not in email.split("@")[-1]:
            result.add_error("email", "Email address must contain a valid domain (e.g., '.com')", "email_missing_domain")
            return result
        
        # Advanced validation using email-validator (but allow test domains)
        try:
            valid_email = validate_email(email, check_deliverability=False)  # Don't check if domain actually exists
            email = valid_email.email
        except EmailNotValidError as e:
            error_str = str(e).lower()
            if "domain" in error_str:
                result.add_error("email", "The domain name in your email address is not valid", "email_invalid_domain")
            elif "local" in error_str:
                result.add_error("email", "The part before '@' in your email address contains invalid characters", "email_invalid_local")
            elif "syntax" in error_str:
                result.add_error("email", "Email address format is not valid", "email_invalid_syntax")
            else:
                result.add_error("email", f"Email address is not valid: {str(e)}", "email_invalid")
            return result
        
        return result
    
    @staticmethod
    def validate_password(password: str, context: str = "signup") -> ValidationResult:
        """Validate password with comprehensive requirements and specific feedback"""
        result = ValidationResult()
        
        if not password:
            result.add_error("password", "Password is required", "password_required")
            return result
        
        # For login, we only check if password exists (don't reveal requirements)
        if context == "login":
            return result
        
        # For signup, provide detailed requirements
        issues = []
        
        # Length requirement
        if len(password) < 8:
            issues.append("be at least 8 characters long")
        
        # Uppercase letter requirement
        if not re.search(r'[A-Z]', password):
            issues.append("contain at least one uppercase letter (A-Z)")
        
        # Lowercase letter requirement  
        if not re.search(r'[a-z]', password):
            issues.append("contain at least one lowercase letter (a-z)")
        
        # Number requirement
        if not re.search(r'[0-9]', password):
            issues.append("contain at least one number (0-9)")
        
        # Check for common weak passwords
        weak_passwords = [
            'password', '12345678', 'qwerty123', 'abc12345', 'password123',
            '11111111', '87654321', 'qwertyui', 'password1', '123456789'
        ]
        
        if password.lower() in weak_passwords:
            issues.append("not be a commonly used password")
        
        if issues:
            if len(issues) == 1:
                message = f"Password must {issues[0]}"
            elif len(issues) == 2:
                message = f"Password must {issues[0]} and {issues[1]}"
            else:
                message = f"Password must {', '.join(issues[:-1])}, and {issues[-1]}"
            
            result.add_error("password", message, "password_requirements")
        
        return result
    
    @staticmethod
    def validate_name(name: str) -> ValidationResult:
        """Validate user name with specific feedback"""
        result = ValidationResult()
        
        if not name or not name.strip():
            result.add_error("name", "Full name is required", "name_required")
            return result
        
        name = name.strip()
        
        if len(name) < 2:
            result.add_error("name", "Name must be at least 2 characters long", "name_too_short")
            return result
        
        if len(name) > 100:
            result.add_error("name", "Name must be less than 100 characters", "name_too_long")
            return result
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", name):
            result.add_error("name", "Name can only contain letters, spaces, hyphens, and apostrophes", "name_invalid_chars")
            return result
        
        return result
    
    @staticmethod
    def validate_registration_data(email: str, password: str, name: str) -> ValidationResult:
        """Validate complete registration data and return combined results"""
        combined_result = ValidationResult()
        
        # Validate each field
        email_result = AuthValidationService.validate_email(email)
        password_result = AuthValidationService.validate_password(password, "signup")
        name_result = AuthValidationService.validate_name(name)
        
        # Combine results
        combined_result.errors.extend(email_result.errors)
        combined_result.errors.extend(password_result.errors)
        combined_result.errors.extend(name_result.errors)
        
        combined_result.is_valid = len(combined_result.errors) == 0
        
        return combined_result


class DetailedAuthenticationError(Exception):
    """Enhanced authentication error that carries detailed validation information"""
    def __init__(self, message: str, validation_result: ValidationResult = None, error_type: str = "validation"):
        self.message = message
        self.validation_result = validation_result
        self.error_type = error_type
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        result = {
            "message": self.message,
            "error_type": self.error_type
        }
        
        if self.validation_result:
            result["validation_errors"] = self.validation_result.errors
            result["field_errors"] = self.validation_result.get_field_errors()
        
        return result
