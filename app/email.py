from flask_mailman import Mail
from flask_mail import Message
from app import mail



def send_application_email(candidate_email, recruiter_email, job_title):
    msg_to_candidate = Message('Job Application Confirmation',
                               recipients=[candidate_email])
    msg_to_candidate.body = f"Dear Candidate,\n\nYou have successfully applied for the job: {job_title}.\n\nBest regards,\nJob Portal Team"
    
    msg_to_recruiter = Message('New Job Application Received',
                               recipients=[recruiter_email])
    msg_to_recruiter.body = f"Dear Recruiter,\n\nA new candidate has applied for your job: {job_title}.\n\nBest regards,\nJob Portal Team"
    
    try:
        mail.send(msg_to_candidate)
        mail.send(msg_to_recruiter)
        print("Emails sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")