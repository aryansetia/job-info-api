from flask import Blueprint, jsonify, request
from app.models import Job, Application, User, db
from app.controllers.auth import token_required
from app.email import send_application_email

candidate_bp = Blueprint('candidate_bp', __name__)


@candidate_bp.route('/jobs', methods=['GET'], endpoint='list_jobs')
@token_required
def list_jobs(current_user_id, current_user_role):
    if current_user_role != 'candidate':
        return jsonify({"message": "Only candidates can view jobs"}), 403

    jobs = Job.query.all()
    jobs_data = [{"id": job.id, "title": job.title,
                  "description": job.description} for job in jobs]

    return jsonify({"jobs": jobs_data}), 200


@candidate_bp.route('/jobs/<int:job_id>/apply', methods=['POST'], endpoint='apply_to_job')
@token_required
def apply_to_job(current_user_id, current_user_role, job_id):
    if current_user_role != 'candidate':
        return jsonify({"message": "Only candidates can apply for jobs"}), 403

    job = Job.query.get(job_id)
    if not job:
        return jsonify({"message": "Job not found"}), 404

    existing_application = Application.query.filter_by(candidate_id=current_user_id, job_id=job_id).first()
    if existing_application:
        return jsonify({"message": "You have already applied to this job"}), 400

    application = Application(job_id=job.id, candidate_id=current_user_id)
    db.session.add(application)
    db.session.commit()

    candidate = User.query.get(current_user_id)
    recruiter = User.query.get(job.recruiter_id)

    send_application_email(candidate.email, recruiter.email, job.title)

    return jsonify({"message": "Successfully applied to the job and notifications sent."}), 200


@candidate_bp.route('/applications', methods=['GET'], endpoint='view_applications')
@token_required
def view_applications(current_user_id, current_user_role):
    if current_user_role != 'candidate':
        return jsonify({"message": "Only candidates can view their applications"}), 403

    applications = Application.query.filter_by(
        candidate_id=current_user_id).all()
    job_ids = [application.job_id for application in applications]
    jobs = Job.query.filter(Job.id.in_(job_ids)).all()

    jobs_data = [{"id": job.id, "title": job.title,
                  "description": job.description} for job in jobs]

    return jsonify({"applied_jobs": jobs_data}), 200
