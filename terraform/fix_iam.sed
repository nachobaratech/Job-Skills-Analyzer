# Comment out IAM role resource
/^resource "aws_iam_role" "lambda_role"/,/^}$/ {
  s/^/# /
}

# Comment out IAM policies
/^resource "aws_iam_role_policy/,/^}$/ {
  s/^/# /
}

# Comment out IAM policy attachment
/^resource "aws_iam_role_policy_attachment" "lambda_logs"/,/^}$/ {
  s/^/# /
}

# Update Lambda role reference
s|role.*= aws_iam_role.lambda_role.arn|role            = "arn:aws:iam::223280412524:role/LabRole"|
