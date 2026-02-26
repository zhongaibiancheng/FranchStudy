# routes/auth.py
from flask import Blueprint, request, jsonify, current_app
import jwt
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash,generate_password_hash

import json
import time, random, string

import uuid
import re

from psycopg2.extras import RealDictCursor
from db import get_db

spellingbee_bp = Blueprint('speelingbee', __name__)