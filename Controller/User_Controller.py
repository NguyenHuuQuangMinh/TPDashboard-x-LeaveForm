from flask import Blueprint,session,redirect,url_for,request, render_template,flash
from Controller.decorators import login_required
from Model.entity import Entity

user_bp = Blueprint('user', __name__)

@user_bp.before_request
@login_required
def before_all():
    pass

@user_bp.route('/home',methods=['GET', 'POST'])
def home():
    code = request.args.get('code', '').strip()
    name = request.args.get('name', '').strip()
    category = request.args.get('category', '').strip()
    tradeshow = request.args.get('tradeshow', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 100
    total, messages = Entity.get_nts(code, name, category, tradeshow, page)
    categories = Entity.get_cate()
    total_pages = (total + per_page - 1) // per_page
    detailscate = Entity.get_nts_detail()
    if session.get('is_admin') == 1:
        session['is_admin'] = 0

    return render_template("user/home.html",  messages=messages,
                           categories=categories,
                           total=total,
                           page=page,
                           total_pages=total_pages,
                           nts_detail=detailscate,
                           filters={'code': code, 'name': name, 'category': category, 'tradeshow': tradeshow})