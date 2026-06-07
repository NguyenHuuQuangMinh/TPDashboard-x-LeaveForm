from flask import Blueprint, session, redirect, url_for, request, render_template, flash, jsonify
from Controller.decorators import login_required
from Model.entity import Entity

partial_bp = Blueprint('partial', __name__)

@partial_bp.before_request
@login_required
def before_all():
    pass

@partial_bp.route('/partial/nts/agent/<code>')
def nts_agent_detail(code):
    contacts, yearly = Entity.get_details(code)
    return jsonify({
        'contacts': [dict(c) for c in contacts],
        'yearly':   [dict(y) for y in yearly]
    })
