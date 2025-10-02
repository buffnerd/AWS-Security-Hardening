# Lambda Build Configuration

This directory contains the build configuration for packaging the AWS Security Toolkit as Lambda functions.

## Files

- `build.sh`: Build script to create Lambda deployment package
- `requirements.txt`: Python dependencies for Lambda runtime
- `README.md`: This documentation file

## Usage

```bash
chmod +x build.sh
./build.sh
```

This will create a `aws-security-toolkit-lambda.zip` file ready for Lambda deployment.