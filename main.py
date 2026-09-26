import flet as ft
import asyncio
import random
import datetime
from PIL import Image, ImageDraw
import io
import base64
import os
import json

# --- GÉNÉRATION DU BADGE WAKANDAIS (PNG SHURI TECH) ---
def get_shuri_badge_b64():
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    points = [(32, 4), (58, 20), (58, 44), (32, 60), (6, 44), (6, 20)]
    draw.polygon(points, fill=(20, 23, 34, 255), outline=(0, 240, 255, 255))
    inner_points = [(32, 14), (48, 24), (48, 40), (32, 50), (16, 40), (16, 24)]
    draw.polygon(inner_points, fill=(123, 44, 191, 255), outline=(255, 215, 0, 255))
    draw.ellipse([28, 28, 36, 36], fill=(0, 240, 255, 255))
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

SHURI_BADGE_BASE64 = get_shuri_badge_b64()


def main(page: ft.Page):
    page.title = "White Wolf Workout"
    page.theme_mode = "dark" 
    page.bgcolor = "#0A0B10"
    
    try:
        page.window.width = 410
        page.window.height = 800
    except Exception:
        pass
    
    page.padding = 0 
    page.scroll = None 

    page.fonts = {
        "Beyno": "Beyno.ttf"
    }

    # --- MÉMOIRE PERSISTANTE INDESTRUCTIBLE (JSON NATIF) ---
    data_dir = os.environ.get("HOME", os.path.abspath("."))
    SAVE_FILE = os.path.join(data_dir, "white_wolf_data.json")

    def load_data():
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "streak": 0,
            "completed_dates": [],
            "total_skipped": 0,
            "total_completed": 0,
            "history": {}
        }

    user_data = load_data()

    def save_data():
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(user_data, f, ensure_ascii=False, indent=4)
        except Exception:
            pass


    # --- DONNÉES & GESTION DU TEMPS ---
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())

    semaine_pattern = ["A", "B", "REPOS", "A", "B", "REPOS", "A"]
    noms_jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

    citations = [
        "Le métal le plus solide se forge dans les flammes les plus chaudes.",
        "Concentre-toi. Chaque répétition construit ta propre armure.",
        "White Wolf pour toujours ! Ne lâche rien sur cette série.",
        "Prends une grande inspiration. Le maté de la victoire n'est plus très loin.",
        "¡Adelante! La faiblesse n'a pas sa place ici.",
        "La gravité est ton ennemie, l'élastique est ton allié.",
        "La discipline pèse des grammes, le regret pèse des tonnes.",
        "La douleur est temporaire, la force est définitive.",
        "Ce n'est pas censé être facile. Sinon tout le monde le ferait.",
        "L'esprit commande, le corps exécute."
    ]

    seances = {
        "A": [
            {"nom": "1. Pompes", "detail": "Mains largeur d'épaules. Descends en gardant les coudes le long du corps à 45°."},
            {"nom": "2. Développé Militaire", "detail": "Pieds sur l'élastique. Poings aux clavicules. Pousse vers le plafond."},
            {"nom": "3. Écartés (Chest Fly)", "detail": "Élastique à la porte, tourne-lui le dos. Bras fléchis, referme-les devant ton sternum."},
            {"nom": "4. Extensions Triceps", "detail": "Élastique à la porte, face à lui. Coudes plaqués aux côtes. Tire vers le bas."},
            {"nom": "5. Hip Thrust (Fessiers)", "detail": "Dos au sol, élastique tendu sur le bassin. Pousse sur les talons et contracte fort les fessiers au sommet."}
        ],
        "B": [
            {"nom": "1. Tirage Dos (Rowing)", "detail": "Assis, élastique derrière les pieds. Dos droit. Tire les coudes en arrière."},
            {"nom": "2. Band Pull-Apart", "detail": "Debout, bras tendus. Écarte les bras en croix pour ramener l'élastique sur la poitrine."},
            {"nom": "3. Curl Biceps", "detail": "Debout sur l'élastique. Coudes plaqués. Remonte les poings vers les épaules."},
            {"nom": "4. Planche Commando", "detail": "Gainage sur les coudes. Monte sur la main droite, puis gauche, puis redescends."},
            {"nom": "5. Soulevé de terre (RDL)", "detail": "Debout sur l'élastique, penche le buste en avant (dos droit). Remonte en contractant fort les fessiers."}
        ]
    }

    # Timer recalibré à 30 secondes
    etat = {"seance": "A", "index": 0, "temps": 30, "en_cours": False, "serie": 1, "phase": "effort", "session_log": []}

    accueil_view = ft.Column(horizontal_alignment="center", scroll="auto", expand=True)
    workout_view = ft.Column(horizontal_alignment="stretch", scroll="auto", expand=True)

    # ==========================================
    #   ARCHITECTURE BLINDÉE (CALQUES ABSOLUS)
    # ==========================================
    bg_container = ft.Container(
        bgcolor="#0A0B10",
        left=0, top=0, right=0, bottom=0 
    )
    
    bg_container.content = ft.Image(
        src="Logo White Wolf.jpg",
        fit="contain", # Remplacement du module par le texte brut pour sécuriser la compilation
        opacity=0.06 
    )

    safe_area_wrapper = ft.SafeArea(expand=True)

    fg_container = ft.Container(
        content=safe_area_wrapper,
        left=0, top=0, right=0, bottom=0,
        padding=15
    )

    root_stack = ft.Stack(
        controls=[bg_container, fg_container],
        expand=True
    )
    page.add(root_stack)


    # ==========================================
    #             ÉCRAN D'ACCUEIL (QG)
    # ==========================================
    def afficher_accueil():
        accueil_view.controls.clear()

        titre_accueil = ft.Text(
            "WHITE WOLF WORKOUT", 
            size=20, 
            weight="bold", 
            color="#00F0FF", 
            text_align="center",
            font_family="Beyno"
        )
        
        stats_panel = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(f"🔥 {user_data['streak']} J", size=13, weight="bold", color="#FFD700", font_family="Consolas"),
                    ft.Text("Streak", size=9, color="#8B95A5")
                ], alignment="center", horizontal_alignment="center"),
                ft.VerticalDivider(color="#2A2D3A"),
                ft.Column([
                    ft.Text(f"◈ {user_data['total_completed']}", size=13, weight="bold", color="#00F0FF", font_family="Consolas"),
                    ft.Text("Validés", size=9, color="#8B95A5")
                ], alignment="center", horizontal_alignment="center"),
                ft.VerticalDivider(color="#2A2D3A"),
                ft.Column([
                    ft.Text(f"⚡ {user_data['total_skipped']}", size=13, weight="bold", color="#FF9900", font_family="Consolas"),
                    ft.Text("Skippés", size=9, color="#8B95A5")
                ], alignment="center", horizontal_alignment="center"),
            ], alignment="spaceAround"),
            bgcolor="#141722", padding=10, border_radius=12, width=370
        )

        cal_row = ft.Row(alignment="center", spacing=5)
        for i in range(7):
            d = start_of_week + datetime.timedelta(days=i)
            d_str = d.strftime("%Y-%m-%d")
            type_seance = semaine_pattern[i]
            
            is_today = (d == today)
            is_done = d_str in user_data["completed_dates"]

            if is_done:
                bg_color = "#141722"
                couleur_texte = "#00F0FF"
                contenu_bas = ft.Image(src=f"data:image/png;base64,{SHURI_BADGE_BASE64}", width=22, height=22)
            elif is_today:
                bg_color = "#7B2CBF"
                couleur_texte = "white"
                font_sz = 9 if type_seance == "REPOS" else 13
                contenu_bas = ft.Text(type_seance, size=font_sz, weight="bold", color="white", font_family="Beyno")
            else:
                bg_color = "#141722"
                couleur_texte = "#8B95A5"
                font_sz = 9 if type_seance == "REPOS" else 13
                contenu_bas = ft.Text(type_seance, size=font_sz, weight="bold", color=couleur_texte, font_family="Beyno")

            boite = ft.Container(
                content=ft.Column([
                    ft.Text(noms_jours[i], size=10, color=couleur_texte, weight="bold", font_family="Beyno"),
                    ft.Text(str(d.day), size=12, color="white", weight="bold", font_family="Consolas"),
                    ft.Container(height=2),
                    contenu_bas
                ], alignment="center", horizontal_alignment="center", spacing=2),
                width=46, height=75, bgcolor=bg_color, border_radius=8,
                padding=4
            )
            cal_row.controls.append(boite)

        today_str = today.strftime("%Y-%m-%d")
        today_index = today.weekday()
        type_du_jour = semaine_pattern[today_index]
        est_fait_aujourdhui = today_str in user_data["completed_dates"]

        if est_fait_aujourdhui:
            info_txt = ft.Text("MISSION DU JOUR ACCOMPLIE", color="#00F0FF", size=12, weight="bold", font_family="Beyno")
            btn_start = ft.Button(content="ARSENAL EN VEILLE", disabled=True)
        elif type_du_jour == "REPOS":
            info_txt = ft.Text("CYCLE DE RÉCUPÉRATION ACTIVE", color="#8B95A5", size=11, weight="bold", font_family="Beyno")
            btn_start = ft.Button(content="VALIDER LA RÉCUP", on_click=valider_journee_repos, bgcolor="#00F0FF", color="black")
        else:
            info_txt = ft.Text(f"PROTOCOLE REQUIS : SÉANCE {type_du_jour}", color="white", size=11, weight="bold", font_family="Beyno")
            btn_start = ft.Button(content="ENGAGER LA SÉANCE", on_click=lambda e: lancer_workout(type_du_jour), bgcolor="#7B2CBF", color="white")

        historique_col = ft.Column(spacing=5, width=370)
        historique_col.controls.append(ft.Text("JOURNAUX DE PERFORMANCE", size=11, color="#8B95A5", weight="bold", font_family="Beyno"))
        
        if not user_data["history"]:
            historique_col.controls.append(ft.Text("Aucun rapport d'entraînement enregistré.", size=12, color="grey", italic=True))
        else:
            for date_key, log in sorted(user_data["history"].items(), reverse=True)[:3]:
                nb_exos = len(log["exercices"])
                card_log = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"DATE: {date_key}", size=11, weight="bold", color="#00F0FF", font_family="Consolas"),
                            ft.Text(f"SÉANCE {log['seance']}", size=11, weight="bold", color="#FFD700", font_family="Beyno")
                        ], alignment="spaceBetween"),
                        ft.Text(f"Mouvements validés : {nb_exos}", size=11, color="#8B95A5", font_family="Consolas")
                    ], spacing=2),
                    bgcolor="#141722", padding=10, border_radius=8
                )
                historique_col.controls.append(card_log)

        accueil_view.controls.extend([
            ft.Container(height=10),
            titre_accueil,
            ft.Container(height=10),
            stats_panel,
            ft.Container(height=15),
            ft.Text("SYNCHRONISATION HEBDOMADAIRE", size=11, color="#8B95A5", weight="bold", font_family="Beyno"),
            ft.Container(height=5),
            cal_row,
            ft.Container(height=20),
            info_txt,
            ft.Container(height=5),
            btn_start,
            ft.Container(height=15),
            historique_col,
            ft.Container(height=20)
        ])
        
        safe_area_wrapper.content = accueil_view
        page.update()

    def valider_journee_repos(e):
        marquer_jour_termine()
        afficher_accueil()

    def marquer_jour_termine():
        today_str = today.strftime("%Y-%m-%d")
        if today_str not in user_data["completed_dates"]:
            user_data["completed_dates"].append(today_str)
            user_data["streak"] += 1
            if etat["session_log"]:
                user_data["history"][today_str] = {
                    "seance": etat["seance"],
                    "exercices": list(etat["session_log"])
                }
        save_data()


    # ==========================================
    #             ÉCRAN D'ENTRAÎNEMENT
    # ==========================================
    titre_seance = ft.Text("", size=16, weight="bold", color="#00F0FF", font_family="Beyno")
    serie_txt = ft.Text("", size=12, weight="bold", color="#FFD700", font_family="Consolas")
    
    checklist_ui = ft.Column()
    checklist_lignes = []

    exo_titre = ft.Text("", size=16, weight="bold", color="white", font_family="Consolas")
    exo_detail = ft.Text("", size=12, color="#8B95A5", italic=True)
    
    reps_input = ft.TextField(value="10", width=70, height=35, text_align="center", text_style=ft.TextStyle(size=14, color="white", weight="bold", font_family="Consolas"))
    reps_row = ft.Row([
        ft.Text("Répétitions réalisées :", size=12, color="#8B95A5"),
        reps_input
    ], alignment="center")

    citation_txt = ft.Text("", size=14, color="#FFD700", italic=True, text_align="center", visible=False)
    # Timer initialisé sur 30s
    chrono_txt = ft.Text("30", size=70, weight="bold", color="#7B2CBF", font_family="Consolas")
    
    btn_play = ft.Button(content="LANCER", bgcolor="#7B2CBF", color="white")
    btn_pause = ft.Button(content="PAUSE", disabled=True, bgcolor="#2A2D3A", color="white")
    btn_skip = ft.Button(content="SAUTER", bgcolor="#333333", color="#FF9900", on_click=lambda e: skip_exercise())
    btn_next = ft.Button(content="SUIVANT", bgcolor="#00F0FF", color="black")
    
    btn_abort = ft.Button(content="ABANDONNER / RETOUR QG", on_click=lambda e: afficher_accueil(), bgcolor="#141722", color="#8B95A5")
    
    controle_row = ft.Row(
        [btn_play, btn_pause, btn_skip, btn_next], 
        alignment="center", 
        spacing=6,
        wrap=True
    )
    abort_row = ft.Row([btn_abort], alignment="center")

    def charger_checklist():
        checklist_lignes.clear()
        checklist_ui.controls.clear()
        for exo in seances[etat["seance"]]:
            ligne = ft.Row([
                ft.Text("○", size=15, color="#00F0FF", weight="bold", font_family="Consolas"),
                ft.Text(exo["nom"], size=13, color="white", font_family="Consolas")
            ], spacing=10)
            checklist_lignes.append(ligne)
            checklist_ui.controls.append(ligne)

    def marquer_exercice_fait(index, statut="fait"):
        ligne = checklist_lignes[index]
        if statut == "fait":
            ligne.controls[0].value = "◈"
            ligne.controls[0].color = "#00F0FF"
        else:
            ligne.controls[0].value = "⚡"
            ligne.controls[0].color = "#FF9900"
            
        ligne.controls[1].decoration = ft.TextDecoration.LINE_THROUGH
        ligne.controls[1].color = "#8B95A5"

    def reinitialiser_checklist():
        for ligne in checklist_lignes:
            ligne.controls[0].value = "○"
            ligne.controls[0].color = "#00F0FF"
            ligne.controls[1].decoration = ft.TextDecoration.NONE
            ligne.controls[1].color = "white"

    def update_ui_workout():
        if etat["phase"] == "effort":
            exo_titre.value = seances[etat["seance"]][etat["index"]]["nom"]
            exo_detail.value = seances[etat["seance"]][etat["index"]]["detail"]
            exo_detail.visible = True
            reps_row.visible = True
            citation_txt.visible = False
        else:
            exo_titre.value = "RÉCUPÉRATION TACTIQUE :"
            exo_titre.font_family = "Beyno"
            
            exo_detail.visible = False
            reps_row.visible = False
            citation_txt.value = f'"{random.choice(citations)}"'
            citation_txt.visible = True
            
        chrono_txt.value = str(etat["temps"])
        serie_txt.value = f"SÉRIE {etat['serie']} / 3"
        page.update()

    def terminer_entrainement():
        exo_titre.value = "MISSION ACCOMPLIE !"
        exo_titre.font_family = "Beyno"
        
        exo_detail.value = "L'armure du White Wolf est renforcée."
        exo_detail.color = "#00F0FF"
        exo_detail.visible = True
        reps_row.visible = False
        citation_txt.visible = False
        chrono_txt.value = "0"
        
        controle_row.visible = False
        btn_abort.content = "RETOURNER AU QG"
        page.update()
        marquer_jour_termine()

    async def run_timer(e):
        etat["en_cours"] = True
        btn_play.disabled = True
        btn_pause.disabled = False
        page.update()
        
        while int(etat["temps"]) > 0 and etat["en_cours"]:
            await asyncio.sleep(1)
            if etat["en_cours"]:
                etat["temps"] = int(etat["temps"]) - 1
                chrono_txt.value = str(etat["temps"])
                page.update()
                
        if etat["en_cours"]:
            etat["en_cours"] = False
            btn_play.disabled = False
            btn_pause.disabled = True
            page.update()

    def pause_timer(e):
        etat["en_cours"] = False
        btn_play.disabled = False
        btn_pause.disabled = True
        page.update()

    def skip_exercise():
        etat["en_cours"] = False
        nom_exo = seances[etat["seance"]][etat["index"]]["nom"]
        etat["session_log"].append({"nom": nom_exo, "reps": 0, "statut": "skippé"})
        
        user_data["total_skipped"] += 1
        save_data() 

        marquer_exercice_fait(etat["index"], statut="skippé")
        etat["index"] += 1
        if etat["index"] >= len(seances[etat["seance"]]):
            etat["index"] = 0
            etat["serie"] += 1
            if etat["serie"] > 3:
                terminer_entrainement()
                return
            else:
                reinitialiser_checklist()
        etat["phase"] = "effort"
        etat["temps"] = 30 
        chrono_txt.color = "#7B2CBF"
        btn_play.disabled = False
        btn_pause.disabled = True
        exo_titre.font_family = "Consolas"
        update_ui_workout()

    def next_step(e):
        etat["en_cours"] = False
        btn_play.disabled = False
        btn_pause.disabled = True
        
        if etat["phase"] == "effort":
            try:
                reps_effectuees = int(reps_input.value)
            except ValueError:
                reps_effectuees = 0

            nom_exo = seances[etat["seance"]][etat["index"]]["nom"]
            etat["session_log"].append({"nom": nom_exo, "reps": reps_effectuees, "statut": "fait"})
            
            user_data["total_completed"] += 1
            save_data() 

            etat["phase"] = "repos"
            etat["temps"] = 15 
            chrono_txt.color = "#00F0FF"
        else:
            marquer_exercice_fait(etat["index"], statut="fait")
            
            etat["index"] += 1
            if etat["index"] >= len(seances[etat["seance"]]):
                etat["index"] = 0
                etat["serie"] += 1
                if etat["serie"] > 3:
                    terminer_entrainement()
                    return
                else:
                    reinitialiser_checklist()
                    
            etat["phase"] = "effort"
            etat["temps"] = 30 
            chrono_txt.color = "#7B2CBF"
            exo_titre.font_family = "Consolas"
            
        update_ui_workout()

    btn_play.on_click = run_timer
    btn_pause.on_click = pause_timer
    btn_next.on_click = next_step

    def lancer_workout(seance_id):
        workout_view.controls.clear()
        
        etat["seance"] = seance_id
        etat["index"] = 0
        etat["temps"] = 30 
        etat["en_cours"] = False
        etat["serie"] = 1
        etat["phase"] = "effort"
        etat["session_log"] = []
        
        btn_play.disabled = False
        btn_next.disabled = False
        controle_row.visible = True
        btn_abort.content = "ABANDONNER / RETOUR QG"
        chrono_txt.color = "#7B2CBF"
        exo_detail.color = "#8B95A5"
        
        titre_seance.value = f"PROTOCOLE SÉANCE {seance_id}"
        exo_titre.font_family = "Consolas"
        
        charger_checklist()
        workout_view.controls.extend([
            ft.Row([titre_seance, serie_txt], alignment="spaceBetween"),
            ft.Divider(color="#2A2D3A"),
            checklist_ui,
            ft.Container(
                content=ft.Column([exo_titre, exo_detail, reps_row, citation_txt], horizontal_alignment="center", spacing=6), 
                padding=16, bgcolor="#141722", border_radius=12, margin=10
            ),
            ft.Row([chrono_txt], alignment="center"),
            ft.Container(height=5),
            controle_row,
            ft.Container(height=5),
            abort_row
        ])
        
        update_ui_workout()
        safe_area_wrapper.content = workout_view
        page.update()

    afficher_accueil()

ft.run(main)
