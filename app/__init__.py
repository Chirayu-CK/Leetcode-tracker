from flask import Flask, render_template, request, redirect, session
from app.leetcode import (
    get_user_stats,
    get_streak_counter,
    get_topic_stats,
    leetcode_readme,
    contestrating,
)
import os
from dotenv import load_dotenv
from supabase import create_client
import secrets, string, random


def generate_room_code(sb):
    """
    Generate a 6-character room code and verify that it is not already
    present in the rooms table.
    """
    try:
        while True:
            code = ''.join(
                random.choices(
                    string.ascii_uppercase + string.digits,
                    k=6
                )
            )

            existing = (
                sb.table("rooms")
                .select("id")
                .eq("join_code", code)
                .execute()
            )

            if not existing.data:
                return code

    except Exception as e:
        print("Room code generation error:", e)
        return None


def create_app():
    load_dotenv()

    app = Flask(__name__)

    # -------------------- Environment / app setup --------------------
    secret_key = os.getenv("FLASK_SECRET_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    if not secret_key:
        raise RuntimeError("FLASK_SECRET_KEY is not set")

    if not supabase_url:
        raise RuntimeError("SUPABASE_URL is not set")

    if not supabase_key:
        raise RuntimeError("SUPABASE_ANON_KEY is not set")

    app.secret_key = secret_key

    try:
        supabase = create_client(supabase_url, supabase_key)
    except Exception as e:
        raise RuntimeError(f"Unable to initialize Supabase client: {e}")


    @app.route("/")
    def home():
        try:
           

            if "user_id" in session:
                
                return redirect("/profile")

            return render_template("home.html")

        except Exception as e:
            
            return "Unable to load home page.", 500



    @app.route("/login")
    def login():
        try:
            redirect_url = os.getenv(
            "OAUTH_REDIRECT_URL",
            "http://localhost:8000/auth/callback"
)

            r = supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": redirect_url,
                    "query_params": {
                        "prompt": "select_account"
                    }
                }
            })

            if not r or not getattr(r, "url", None):
                return "Unable to start Google login.", 500

            return redirect(r.url)

        except Exception as e:
            
            return "Unable to start login. Please try again.", 500

    @app.route("/logout")
    def logout():
        try:
            sb = get_supabase()

            if sb is not None:
                try:
                    sb.auth.sign_out()
                   
                except Exception as e:
                    print("Supabase logout error:", e)

            session.clear()
            return redirect("/")

        except Exception as e:
            print("Logout error:", e)
            session.clear()
            return redirect("/")

    def get_supabase():
        try:
            access_token = session.get("access_token")
            refresh_token = session.get("refresh_token")

            if not access_token or not refresh_token:
                return None

            sb = create_client(
                os.getenv("SUPABASE_URL"),
                os.getenv("SUPABASE_ANON_KEY")
            )

            sb.auth.set_session(access_token, refresh_token)
            return sb

        except Exception as e:
            print("Supabase session error:", e)
            return None


    @app.route("/auth/callback")
    def auth_callback():

      
        code = request.args.get("code")


        if not code:
            print("ERROR: No authorization code received")
            return "No authorization code received.", 400

        try:
            # Exchange OAuth code for Supabase session
            response = supabase.auth.exchange_code_for_session({
                "auth_code": code
            })

           

            if not response or not response.user or not response.session:
                print("ERROR: Invalid authentication response")
                return "Authentication failed. Invalid authentication response.", 400

            user = response.user

            if not user.id:
                # print("ERROR: User ID missing")
                return "Authentication failed. User ID missing.", 400

            # Store login information in Flask session
            session["user_id"] = user.id
            session["email"] = user.email
            session["access_token"] = response.session.access_token
            session["refresh_token"] = response.session.refresh_token

           
            # Check if profile already exists
            existing_profile = (
                supabase
                .table("profiles")
                .select("*")
                .eq("id", user.id)
                .execute()
            )

           

            # -----------------------------------------
            # NEW USER
            # -----------------------------------------
            if not existing_profile.data:

                print("NEW USER - creating profile")

                verification_key = secrets.token_urlsafe(12)
                session["lee_verification_key"] = verification_key

                try:
                    supabase.table("profiles").insert({
                        "id": user.id,
                        "email": user.email
                    }).execute()

                except Exception as e:
                    print("Profile creation error:", e)
                    session.clear()

                    return (
                        "Unable to create your profile. "
                        "Please try again.",
                        500
                    )

                print("REDIRECTING NEW USER TO LEETCODE CONNECTION")

                return render_template(
                    "connect_leetcode.html",
                    email=user.email,
                    verification_key=verification_key
                )

            # -----------------------------------------
            # EXISTING USER
            # -----------------------------------------
            profile = existing_profile.data[0]

           

            # User exists but LeetCode is not verified
            if not profile.get("leetcode_verified"):

                

                if "lee_verification_key" not in session:
                    verification_key = secrets.token_urlsafe(12)
                    session["lee_verification_key"] = verification_key
                else:
                    verification_key = session["lee_verification_key"]

                return render_template(
                    "connect_leetcode.html",
                    email=user.email,
                    verification_key=verification_key
                )

            # Get linked LeetCode username
            username = profile.get("leetcode_username")

           

            if not username:
                
                return redirect("/connect_leetcode")

            # Everything is valid
          

            return redirect("/profile")

        except Exception as e:

          
            session.clear()

            return (
                "Authentication failed. "
                "Please try logging in again.",
                400
            )

    

    @app.route("/profile", methods=["GET", "POST"])
    def profile():
        if "user_id" not in session:
            return redirect("/login")

        try:
            result = (
                supabase
                .table("profiles")
                .select("*")
                .eq("id", session["user_id"])
                .execute()
            )

            if not result.data:
                session.clear()
                return redirect("/login")

            profile = result.data[0]

            if not profile.get("leetcode_verified"):
                return redirect("/connect_leetcode")

            username = profile.get("leetcode_username")

            if not username:
                return redirect("/connect_leetcode")

            # Fetch LeetCode data safely.
            try:
                stats = get_user_stats(username)
                streak_stats = get_streak_counter(username)
                topic_stats = get_topic_stats(username)
            except Exception as e:
                print("LeetCode profile fetch error:", e)
                return "Unable to fetch LeetCode data. Please try again later.", 503

            if stats is None or streak_stats is None:
                return "Unable to fetch LeetCode data. Please try again later.", 503

            if topic_stats is None:
                topic_stats = {}

            sb = get_supabase()

            if sb is None:
                session.clear()
                return redirect("/login")

            rooms = []

            try:
                member_rooms = (
                    sb
                    .table("room_members")
                    .select("room_id")
                    .eq("user_id", session["user_id"])
                    .execute()
                )

                for item in (member_rooms.data or []):
                    room_id = item.get("room_id")

                    if not room_id:
                        continue

                    room_result = (
                        sb
                        .table("rooms")
                        .select("id, name, join_code")
                        .eq("id", room_id)
                        .execute()
                    )

                    if room_result.data:
                        rooms.append(room_result.data[0])

            except Exception as e:
                print("Room loading error:", e)
                # Do not crash the whole profile just because rooms failed.
                rooms = []

            return render_template(
                "profile.html",
                username=username,
                stats=stats,
                streak_stats=streak_stats,
                topic_stats=topic_stats,
                room=rooms
            )

        except Exception as e:
            print("Profile error:", e)
            return "Unable to load your profile. Please try again.", 500


    @app.route("/connect_leetcode")
    def connect_leetcode():
        if "user_id" not in session:
            return redirect("/login")

        try:
            # Regenerate a key if the session no longer has one.
            if not session.get("lee_verification_key"):
                session["lee_verification_key"] = secrets.token_urlsafe(12)

            return render_template(
                "connect_leetcode.html",
                email=session.get("email"),
                verification_key=session.get("lee_verification_key")
            )

        except Exception as e:
            print("Connect LeetCode page error:", e)
            return "Unable to load LeetCode verification page.", 500


    @app.route("/verify_leetcode", methods=["POST"])
    def verify_leetcode():
        if "user_id" not in session:
            return redirect("/login")

        username = (request.form.get("username") or "").strip()

        if not username:
            return "Please enter a LeetCode username.", 400

        verification_key = session.get("lee_verification_key")

        if not verification_key:
            return "Verification session expired. Please login again.", 400

        try:
            readme = leetcode_readme(username)
        except Exception as e:
            print("LeetCode verification fetch error:", e)
            return "Unable to contact LeetCode. Please try again later.", 503

        if readme is None:
            return "LeetCode user not found.", 404

        if verification_key not in readme:
            return (
                "Verification key not found. "
                "Please add the key to your LeetCode profile.",
                400
            )

        try:
            r = (
                supabase
                .table("profiles")
                .update({
                    "leetcode_verified": True,
                    "leetcode_username": username
                })
                .eq("id", session["user_id"])
                .execute()
            )

            if not r.data:
                return "Unable to update LeetCode verification.", 500

            check = (
                supabase
                .table("profiles")
                .select("*")
                .eq("id", session["user_id"])
                .execute()
            )

            if not check.data:
                return "Unable to confirm LeetCode verification.", 500

        except Exception as e:
            print("LeetCode verification database error:", e)
            return "Unable to save LeetCode verification. Please try again.", 500

        session.pop("lee_verification_key", None)

        try:
            stats = get_user_stats(username)
            streak_stats = get_streak_counter(username)
            topic_stats = get_topic_stats(username)
        except Exception as e:
            print("Post-verification LeetCode fetch error:", e)
            return redirect("/profile")

        if stats is None or streak_stats is None:
            return redirect("/profile")

        if topic_stats is None:
            topic_stats = {}

        return render_template(
            "profile.html",
            username=username,
            stats=stats,
            streak_stats=streak_stats,
            topic_stats=topic_stats,
            room=[]
        )


    @app.route("/create-room", methods=["GET", "POST"])
    def create_room():
        if "user_id" not in session:
            return redirect("/login")

        if request.method == "GET":
            try:
                return render_template("create_room.html")
            except Exception as e:
                print("Create room page error:", e)
                return "Unable to load create room page.", 500

        room_name = (request.form.get("room_name") or "").strip()

        if not room_name:
            return "Room name cannot be empty.", 400

        if len(room_name) > 100:
            return "Room name is too long.", 400

        sb = get_supabase()

        if sb is None:
            session.clear()
            return redirect("/login")

        try:
            code = generate_room_code(sb)

            if not code:
                return "Unable to generate a room code. Please try again.", 500

            room = (
                sb
                .table("rooms")
                .insert({
                    "name": room_name,
                    "join_code": code,
                    "created_by": session["user_id"]
                })
                .execute()
            )

            if not room.data:
                return "Unable to create room. Please try again.", 500

            room_id = room.data[0].get("id")

            if not room_id:
                return "Room was created but its ID could not be retrieved.", 500

            try:
                sb.table("room_members").insert({
                    "room_id": room_id,
                    "user_id": session["user_id"]
                }).execute()

            except Exception as e:
                print("Room membership creation error:", e)

                # Clean up the room if creator membership could not be added.
                try:
                    sb.table("rooms").delete().eq("id", room_id).execute()
                except Exception as cleanup_error:
                    print("Room cleanup error:", cleanup_error)

                return "Unable to add you to the room. Please try again.", 500

            return redirect("/profile")

        except Exception as e:
            print("Create room error:", e)
            return "Unable to create room. Please try again.", 500


    @app.route("/join-room", methods=["GET", "POST"])
    def join_room():
        if "user_id" not in session:
            return redirect("/login")

        if request.method == "GET":
            try:
                return render_template("join_room.html")
            except Exception as e:
                print("Join room page error:", e)
                return "Unable to load join room page.", 500

        code = (request.form.get("join_code") or "").strip().upper()

        if not code:
            return "Please enter a room code.", 400

        if len(code) != 6:
            return "Room code must be 6 characters.", 400

        allowed = set(string.ascii_uppercase + string.digits)
        if any(char not in allowed for char in code):
            return "Invalid room code format.", 400

        sb = get_supabase()

        if sb is None:
            session.clear()
            return redirect("/login")

        try:
            room = (
                sb
                .table("rooms")
                .select("id, name")
                .eq("join_code", code)
                .execute()
            )

            if not room.data:
                return "Invalid room code.", 404

            room_id = room.data[0].get("id")

            if not room_id:
                return "Invalid room data.", 500

            existing = (
                sb
                .table("room_members")
                .select("room_id")
                .eq("room_id", room_id)
                .eq("user_id", session["user_id"])
                .execute()
            )

            if existing.data:
                return "You are already in this room.", 409

            sb.table("room_members").insert({
                "room_id": room_id,
                "user_id": session["user_id"]
            }).execute()

            return redirect("/profile")

        except Exception as e:
            print("Join room error:", e)

            # A database UNIQUE constraint may raise here if two join
            # requests happen at nearly the same time.
            message = str(e).lower()

            if "duplicate" in message or "unique" in message:
                return "You are already in this room.", 409

            return "Unable to join room. Please try again.", 500


    @app.route("/room/<room_id>")
    def list_rooms(room_id):
        if "user_id" not in session:
            return redirect("/login")

        if not room_id:
            return "Invalid room.", 400

        sb = get_supabase()

        if sb is None:
            session.clear()
            return redirect("/login")

        try:
            # Make sure the room exists.
            room_check = (
                sb
                .table("rooms")
                .select("id")
                .eq("id", room_id)
                .execute()
            )

            if not room_check.data:
                return "Room not found.", 404

            # Make sure the current user belongs to this room.
            membership = (
                sb
                .table("room_members")
                .select("room_id")
                .eq("room_id", room_id)
                .eq("user_id", session["user_id"])
                .execute()
            )

            if not membership.data:
                return "You are not a member of this room.", 403

            members = (
                sb
                .table("room_members")
                .select("user_id")
                .eq("room_id", room_id)
                .execute()
            )

            ranking = []

            for member in (members.data or []):
                user_id = member.get("user_id")

                if not user_id:
                    continue

                try:
                    profile = (
                        sb
                        .table("profiles")
                        .select("leetcode_username")
                        .eq("id", user_id)
                        .single()
                        .execute()
                    )

                    if not profile.data:
                        continue

                    username = profile.data.get("leetcode_username")

                    if not username:
                        continue

                    try:
                        rating = contestrating(username)
                    except Exception as e:
                        print(f"Contest rating error for {username}:", e)
                        rating = None

                    # Keep the user visible even if LeetCode rating fetch fails.
                    ranking.append({
                        "username": username,
                        "rating": rating
                    })

                except Exception as e:
                    print(f"Room member profile error for {user_id}:", e)
                    continue

            # None ratings go to the bottom instead of crashing comparison.
            ranking.sort(
                key=lambda x: (
                    x["rating"] is not None,
                    x["rating"] if x["rating"] is not None else float("-inf")
                ),
                reverse=True
            )

            for i, user in enumerate(ranking):
                user["rank"] = i + 1

            return render_template(
                "room.html",
                ranking=ranking
            )

        except Exception as e:
            print("Room page error:", e)
            return "Unable to load room. Please try again.", 500


    # -------------------- Generic Flask errors --------------------

    @app.errorhandler(404)
    def not_found(error):
        return "Page not found.", 404


    @app.errorhandler(405)
    def method_not_allowed(error):
        return "Method not allowed.", 405


    @app.errorhandler(500)
    def internal_error(error):
        print("Unhandled server error:", error)
        return "Something went wrong on the server.", 500


    return app
