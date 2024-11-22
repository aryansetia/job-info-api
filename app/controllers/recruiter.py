from flask import Blueprint, request, jsonify
from app import db
from app.models import Job, Application, User
from app.controllers.auth import token_required  

recruiter_bp = Blueprint('recruiter_bp', __name__)


@recruiter_bp.route('/jobs', methods=['POST'])
@token_required
def post_job(current_user_id, current_user_role):
    if current_user_role != 'recruiter':
        return jsonify({"message": "Only recruiters can post jobs"}), 403

    data = request.get_json()

    title = data.get('title')
    description = data.get('description')

    if not isinstance(title, str) or not isinstance(description, str):
        return jsonify({"message": "Both title and description must be strings"}), 400

    if not title or not description:
        return jsonify({"message": "Job title and description are required"}), 400

    new_job = Job(title=title, description=description,
                  recruiter_id=current_user_id)
    db.session.add(new_job)
    db.session.commit()

    return jsonify({"message": f"Job posted successfully, the job_id is {new_job.id}"}), 201


@recruiter_bp.route('/jobs/<int:job_id>/applicants', methods=['GET'], endpoint='view_applicants')
@token_required
def view_applicants(current_user_id, current_user_role, job_id):
    if current_user_role != 'recruiter':
        return jsonify({"message": "Only recruiters can view applicants"}), 403

    job = Job.query.get(job_id)
    if not job:
        return jsonify({"message": "Job not found"}), 404


    if int(job.recruiter_id) != int(current_user_id):
        return jsonify({"message": "You are not authorized to view applicants for this job"}), 403

    applicants = Application.query.filter_by(job_id=job_id).all()

    # Manually create the dictionary representation
    applicants_data = [
        {
            "id": applicant.id,
            "job_id": applicant.job_id,
            "candidate_id": applicant.candidate_id,
            "applied_at": applicant.applied_at,
            # Include additional fields if necessary
        }
        for applicant in applicants
    ]

    return jsonify({"job_id": job_id, "applicants": applicants_data}), 200
