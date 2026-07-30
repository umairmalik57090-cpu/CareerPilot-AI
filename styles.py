def get_custom_css() -> str:
    return """
    <style>
        :root {
            color-scheme: dark;
        }

        .stApp {
            background: linear-gradient(135deg, #07111f 0%, #151b4d 45%, #3a1a6d 100%);
            color: #f5f7ff;
        }

        .stAppHeader, .stMainBlockContainer {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            background: rgba(8, 13, 28, 0.84);
            border-right: 1px solid rgba(255,255,255,0.08);
            backdrop-filter: blur(22px);
        }

        .topbar-card, .hero-panel, .dashboard-card, .metric-card, .upload-zone {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 24px;
            box-shadow: 0 20px 45px rgba(0,0,0,0.2);
            backdrop-filter: blur(22px);
        }

        .topbar-card {
            padding: 1.4rem 1.6rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }

        .hero-panel {
            padding: 2rem;
            margin-bottom: 1.4rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
        }

        .hero-title {
            font-size: 2rem;
            font-weight: 800;
            margin: 0.1rem 0;
            color: #f8fbff;
        }

        .hero-subtitle {
            color: #c6d4ff;
            margin: 0;
            max-width: 675px;
        }

        .eyebrow {
            color: #84a8ff;
            text-transform: uppercase;
            letter-spacing: 0.18em;
            font-size: 0.78rem;
            font-weight: 700;
        }

        .topbar-meta {
            display: flex;
            gap: 0.6rem;
            flex-wrap: wrap;
            justify-content: flex-end;
        }

        .meta-pill {
            background: rgba(255,255,255,0.1);
            border-radius: 999px;
            padding: 0.45rem 0.75rem;
            color: #eef3ff;
            font-size: 0.9rem;
        }

        .hero-actions {
            display: flex;
            gap: 0.8rem;
            flex-wrap: wrap;
        }

        .btn-primary, .btn-secondary {
            padding: 0.7rem 1rem;
            border-radius: 999px;
            text-decoration: none;
            font-weight: 700;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .btn-primary {
            background: linear-gradient(90deg, #4f7cff, #8c63ff);
            color: white;
            box-shadow: 0 8px 22px rgba(79, 124, 255, 0.25);
        }

        .btn-secondary {
            background: rgba(255,255,255,0.14);
            color: #f3f6ff;
        }

        .btn-primary:hover, .btn-secondary:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(79, 124, 255, 0.30);
        }

        .stButton > button {
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
        }

        .dashboard-card, .metric-card, .upload-zone {
            padding: 1.2rem;
            margin-bottom: 1rem;
        }

        .dashboard-card h4, .metric-card .metric-label {
            margin-top: 0;
            margin-bottom: 0.25rem;
            color: #f7fbff;
        }

        .dashboard-card p, .metric-card .metric-foot {
            color: #bfd0ff;
            margin-bottom: 0;
        }

        .section-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #f6faff;
            margin: 1.25rem 0 0.7rem;
        }

        .upload-zone {
            text-align: center;
            min-height: 220px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border-style: dashed;
        }

        .upload-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }

        .metric-card {
            text-align: left;
        }

        .metric-value {
            font-size: 1.8rem;
            font-weight: 800;
            color: #ffffff;
            margin: 0.3rem 0;
        }

        .card-icon {
            font-size: 1.3rem;
            margin-bottom: 0.5rem;
        }

        .sidebar-title {
            font-size: 0.88rem;
            font-weight: 700;
            color: #88a6ff;
            margin-bottom: 0.35rem;
            text-transform: uppercase;
            letter-spacing: 0.14em;
        }

        .sidebar-footer {
            color: #8da4ff;
            font-size: 0.92rem;
            line-height: 1.5;
        }

        .st-emotion-cache-1wmy9hl, .st-emotion-cache-1v0mbdj {
            background: transparent;
        }

        div[data-testid="stVerticalBlock"] > div {
            gap: 0.4rem;
        }

        button[kind="primary"] {
            border-radius: 999px;
        }

        .stDownloadButton > button {
            border-radius: 999px;
        }

        iframe[data-testid="stCustomComponentV1"], iframe {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
    </style>
    """
