import streamlit as st
import requests
import json
import pandas as pd
import time
import base64
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional, Union, Tuple

# アプリケーション設定
class Config:
    # デフォルト値
    DEFAULT_API_BASE_URL = "http://localhost:8080"
    APP_TITLE = "Cash Point Pay マネジメントシステム"
    SESSION_COOKIE = "cash_point_pay_session"

    # 各種エンドポイント
    ENDPOINTS = {
        "login": "/api/login",
        "logout": "/api/logOut",
        "pay": "/api/pay",
        "payment": "/api/payment",
        "pos_pay": "/api/POS/pay",
        "pos_payment": "/api/POS/payment",
        "query": "/api/query",
        "machine_info": "/api/machineInfo",
        "door_control": "/api/doorControl",
        "cash_info": "/api/cashInfo",
        "cash_detail_info": "/api/cashDetailInfo",
        "refill": "/api/refill",
        "refill_end": "/api/refillend",
        "refund": "/api/refund",
        "withdraw": "/api/withdraw",
        "cancel": "/api/cancel",
        "payment_stop": "/api/paymentStop",
        "payment_continue": "/api/paymentContinue",
        "sensor_status": "/api/sensorStatus",
        "cassette_status": "/api/cassetteStatus",
        "pd_calibration": "/api/pdCalibration",
        "reset_cassette": "/api/resetCassette",
        "reset_coin_box": "/api/resetCoinBox",
        "drum_to_cassette": "/api/drumToCassette",
        "get_status": "/api/getStatus",
        "reset_status": "/api/resetStatus",
        "self_test": "/api/selfTest",
        "banknote_denomination_setup_get": "/api/banknoteDenominationSetup",
        "banknote_denomination_setup_post": "/api/banknoteDenominationSetup",
        "coin_tube_setup_get": "/api/coinTubeSetup",
        "coin_tube_setup_post": "/api/coinTubeSetup",
        "set_device_setting": "/api/setDeviceSetting",
        "get_error_message": "/api/getErrorMessage",
        "setup_setting": "/api/setupSetting",
        "clear_hopper": "/api/clearHopper"
    }

    # APIエラーコードとメッセージのマッピング
    ERROR_CODES = {
        400: "アカウントまたはパスワードが間違っています",
        401: "まだログインしていません",
        500: "不明なエラーが発生しました",
        501: "無効なフォーマットです",
        502: "ホームページに変更してください",
        503: "UUIDが存在しません",
        504: "このAPIはRechargeではありません",
        505: "モーターが実行中です。後でもう一度お試しください",
        506: "在庫不足",
        507: "取引処理中ではありません！",
        508: "紙幣モジュールの準備ができていません。後でもう一度お試しください",
        509: "drumId>=1かつdrumId<=4かつpcs >= 1",
        510: "ドラム内の紙幣の数が0であり、アクションを完了するのに十分ではありません",
        511: "設定が進行中です。設定をキャンセルしてください",
        512: "トランザクションが進行中です。トランザクションをキャンセルまたは停止してください！",
        513: "金額は0より大きくなければなりません",
        514: "硬貨モジュールの準備ができていません。後でもう一度お試しください",
        515: "他のAPIが現在使用中です"
    }

# API接続を管理するクラス
class CashPointPayAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def make_url(self, endpoint: str) -> str:
        """APIエンドポイントの完全なURLを生成"""
        return f"{self.base_url}{endpoint}"

    def handle_response(self, response: requests.Response) -> Dict:
        """APIレスポンスの処理とエラーハンドリング"""
        try:
            data = response.json()
            if not data.get("isSuccess", False):
                st.error(f"APIエラー: {data.get('errorMsg', '不明なエラー')}")
            return data
        except json.JSONDecodeError:
            st.error(f"応答の解析に失敗しました: {response.text}")
            return {"isSuccess": False, "errorMsg": "応答の解析に失敗しました"}

    def login(self, account: str, password: str) -> Dict:
        """システムにログイン"""
        url = self.make_url(Config.ENDPOINTS["login"])
        payload = {"account": account, "password": password}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)

    def logout(self) -> Dict:
        """システムからログアウト"""
        url = self.make_url(Config.ENDPOINTS["logout"])
        response = self.session.get(url)
        return self.handle_response(response)

    def pay(self, items: List[Dict[str, Any]]) -> Dict:
        """支払い処理を開始"""
        url = self.make_url(Config.ENDPOINTS["pay"])
        payload = {"items": items}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)

    def payment(self, amount: str) -> Dict:
        """指定金額の支払い処理を開始"""
        url = self.make_url(Config.ENDPOINTS["payment"])
        payload = {"amount": amount}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)

    def pos_pay(self, items: List[Dict[str, Any]], pos_reference_number: str) -> Dict:
        """POS参照番号付きの支払い処理を開始"""
        url = self.make_url(Config.ENDPOINTS["pos_pay"])
        payload = {"items": items, "POS_reference_number": pos_reference_number}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)

    def pos_payment(self, amount: str, pos_reference_number: str) -> Dict:
        """POS参照番号付きの指定金額支払い処理を開始"""
        url = self.make_url(Config.ENDPOINTS["pos_payment"])
        payload = {"amount": amount, "POS_reference_number": pos_reference_number}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)

    def query(self, uuid: str) -> Dict:
        """取引状態を照会"""
        url = self.make_url(Config.ENDPOINTS["query"])
        payload = {"uuid": uuid}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)

    def get_machine_info(self) -> Dict:
        """機器情報を取得"""
        url = self.make_url(Config.ENDPOINTS["machine_info"])
        response = self.session.get(url)
        return self.handle_response(response)

    def door_control(self, door_settings: Dict[str, str], timeout: int = 10) -> Dict:
        """ドアロックを制御"""
        url = self.make_url(Config.ENDPOINTS["door_control"])
        payload = {**door_settings, "Open Timeout": timeout}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)

    def get_cash_info(self) -> Dict:
        """現金情報を取得"""
        url = self.make_url(Config.ENDPOINTS["cash_info"])
        response = self.session.get(url)
        return self.handle_response(response)

    def get_cash_detail_info(self, name: str) -> Dict:
        """指定したドラムの詳細情報を取得"""
        url = self.make_url(Config.ENDPOINTS["cash_detail_info"])
        payload = {"name": name}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)

    def refill(self) -> Dict:
        """現金モジュールの補充プロセスを開始"""
        url = self.make_url(Config.ENDPOINTS["refill"])
        response = self.session.post(url)
        return self.handle_response(response)

    def refill_end(self) -> Dict:
        """現金モジュールの補充プロセスを終了"""
        url = self.make_url(Config.ENDPOINTS["refill_end"])
        response = self.session.post(url)
        return self.handle_response(response)

    def refund(self, amount: str) -> Dict:
        """指定金額を払い戻し"""
        url = self.make_url(Config.ENDPOINTS["refund"])
        payload = {"amount": amount}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)

    def withdraw(self, withdraw_items: List[Dict[str, Any]]) -> Dict:
        """指定した紙幣・硬貨を引き出し"""
        url = self.make_url(Config.ENDPOINTS["withdraw"])
        payload = {"withdraw": withdraw_items}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)

    def cancel(self) -> Dict:
        """進行中の支払いをキャンセル"""
        url = self.make_url(Config.ENDPOINTS["cancel"])
        response = self.session.post(url)
        return self.handle_response(response)

    def payment_stop(self) -> Dict:
        """現在のトランザクションを完了"""
        url = self.make_url(Config.ENDPOINTS["payment_stop"])
        response = self.session.post(url)
        return self.handle_response(response)

    def payment_continue(self) -> Dict:
        """一時停止したトランザクションを再開"""
        url = self.make_url(Config.ENDPOINTS["payment_continue"])
        response = self.session.post(url)
        return self.handle_response(response)

    def get_sensor_status(self) -> Dict:
        """モジュールのセンサー状態を取得"""
        url = self.make_url(Config.ENDPOINTS["sensor_status"])
        response = self.session.get(url)
        return self.handle_response(response)

    def get_cassette_status(self) -> Dict:
        """カセットの状態を取得"""
        url = self.make_url(Config.ENDPOINTS["cassette_status"])
        response = self.session.get(url)
        return self.handle_response(response)

    def pd_calibration(self) -> Dict:
        """紙幣モジュールの位置検出器キャリブレーション"""
        url = self.make_url(Config.ENDPOINTS["pd_calibration"])
        response = self.session.post(url)
        return self.handle_response(response)

    def reset_cassette(self) -> Dict:
        """カセットのカウントをリセット"""
        url = self.make_url(Config.ENDPOINTS["reset_cassette"])
        response = self.session.post(url)
        return self.handle_response(response)

    def reset_coin_box(self) -> Dict:
        """コインボックスのカウントをリセット"""
        url = self.make_url(Config.ENDPOINTS["reset_coin_box"])
        response = self.session.post(url)
        return self.handle_response(response)

    def drum_to_cassette(self, drum_id: int, pcs: int) -> Dict:
        """ドラムからカセットに紙幣を移動"""
        url = self.make_url(Config.ENDPOINTS["drum_to_cassette"])
        payload = {"drumId": drum_id, "pcs": pcs}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)

    def get_status(self) -> Dict:
        """システムの現在の状態を取得"""
        url = self.make_url(Config.ENDPOINTS["get_status"])
        response = self.session.get(url)
        return self.handle_response(response)

    def reset_status(self) -> Dict:
        """機器のステータスをスタンバイに戻す"""
        url = self.make_url(Config.ENDPOINTS["reset_status"])
        response = self.session.get(url)
        return self.handle_response(response)

    def self_test(self) -> Dict:
        """紙幣・硬貨モジュールの自己診断テスト"""
        url = self.make_url(Config.ENDPOINTS["self_test"])
        response = self.session.get(url)
        return self.handle_response(response)

    def get_banknote_denomination_setup(self) -> Dict:
        """紙幣モジュールの額面設定情報を取得"""
        url = self.make_url(Config.ENDPOINTS["banknote_denomination_setup_get"])
        response = self.session.get(url)
        return self.handle_response(response)

    def set_banknote_denomination_setup(self, settings: List[Dict[str, Any]]) -> Dict:
        """紙幣モジュールの額面設定を構成"""
        url = self.make_url(Config.ENDPOINTS["banknote_denomination_setup_post"])
        response = self.session.post(url, json=settings)
        return self.handle_response(response)

    def get_coin_tube_setup(self) -> Dict:
        """硬貨モジュールの設定情報を取得"""
        url = self.make_url(Config.ENDPOINTS["coin_tube_setup_get"])
        response = self.session.get(url)
        return self.handle_response(response)

    def set_coin_tube_setup(self, settings: List[Dict[str, Any]]) -> Dict:
        """硬貨モジュールの設定を構成"""
        url = self.make_url(Config.ENDPOINTS["coin_tube_setup_post"])
        response = self.session.post(url, json=settings)
        return self.handle_response(response)

    def set_device_setting(self, device_id: str, url: str) -> Dict:
        """デバイス設定を構成"""
        url_endpoint = self.make_url(Config.ENDPOINTS["set_device_setting"])
        payload = {"deviceId": device_id, "url": url}
        response = self.session.post(url_endpoint, json=payload)
        return self.handle_response(response)

    def get_error_message(self, error_code: str) -> Dict:
        """エラーコードに対応するエラーメッセージを取得"""
        url = self.make_url(Config.ENDPOINTS["get_error_message"])
        payload = {"errorCode": error_code}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)

    def setup_setting(self, name: str, value: int) -> Dict:
        """ユーザー設定を構成"""
        url = self.make_url(Config.ENDPOINTS["setup_setting"])
        payload = {"name": name, "value": value}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)

    def clear_hopper(self, hopper_id: int) -> Dict:
        """ホッパーをクリア"""
        url = self.make_url(Config.ENDPOINTS["clear_hopper"])
        payload = {"hopperId": hopper_id}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)

# UIコンポーネントとページ機能
class UI:
    @staticmethod
    def set_page_config():
        """ページの基本設定"""
        st.set_page_config(
            page_title=Config.APP_TITLE,
            page_icon="💰",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # カスタムCSS
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E3A8A;
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #E5E7EB;
        }
        .info-box {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .info-box-success {
            background-color: #D1FAE5;
            border: 1px solid #10B981;
        }
        .info-box-warning {
            background-color: #FEF3C7;
            border: 1px solid #F59E0B;
        }
        .info-box-error {
            background-color: #FEE2E2;
            border: 1px solid #EF4444;
        }
        .sidebar-header {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        .card {
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            background-color: white;
            margin-bottom: 1rem;
        }
        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            color: #1E3A8A;
        }
        .metrics-container {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
        }
        .metric-card {
            flex: 1;
            min-width: 200px;
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #F3F4F6;
            text-align: center;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #1E3A8A;
        }
        .metric-label {
            font-size: 0.875rem;
            color: #6B7280;
        }
        .btn-primary {
            background-color: #1E3A8A;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            font-weight: 600;
            border: none;
            cursor: pointer;
        }
        .btn-primary:hover {
            background-color: #172563;
        }
        .btn-secondary {
            background-color: #6B7280;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            font-weight: 600;
            border: none;
            cursor: pointer;
        }
        .btn-secondary:hover {
            background-color: #4B5563;
        }
        .btn-success {
            background-color: #10B981;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            font-weight: 600;
            border: none;
            cursor: pointer;
        }
        .btn-success:hover {
            background-color: #057851;
        }
        .btn-danger {
            background-color: #EF4444;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            font-weight: 600;
            border: none;
            cursor: pointer;
        }
        .btn-danger:hover {
            background-color: #C81E1E;
        }
        .status-label {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .status-success {
            background-color: #D1FAE5;
            color: #065F46;
        }
        .status-warning {
            background-color: #FEF3C7;
            color: #92400E;
        }
        .status-error {
            background-color: #FEE2E2;
            color: #B91C1C;
        }
        .footer {
            text-align: center;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #E5E7EB;
            font-size: 0.875rem;
            color: #6B7280;
        }
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #F3F4F6; /* ログインページ全体の背景色 */
        }
        .login-card {
            width: 450px; /* カードの幅を調整 */
            padding: 2.5rem; /* パディングを大きく */
            border-radius: 0.75rem; /* 角をより丸く */
            box-shadow: 0 6px 10px -2px rgba(0, 0, 0, 0.15), 0 3px 7px -2px rgba(0, 0, 0, 0.08); /* 影を調整 */
            background-color: white;
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out; /* ホバー効果を追加 */
        }
        .login-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 12px -2px rgba(0, 0, 0, 0.2), 0 4px 8px -2px rgba(0, 0, 0, 0.12);
        }
        .login-title {
            font-size: 2rem; /* タイトルを大きく */
            font-weight: 700; /* タイトルを太く */
            margin-bottom: 2rem; /* マージンを大きく */
            color: #1E3A8A;
            text-align: center;
        }
        .login-input {
            padding: 0.75rem; /* 入力フィールドのパディングを調整 */
            border-radius: 0.375rem; /* 角を丸く */
            border: 1px solid #D1D5DB; /* ボーダーの色を変更 */
            margin-bottom: 1.5rem; /* マージンを大きく */
            width: 100%; /* 幅を100%に */
            font-size: 1rem; /* フォントサイズを大きく */
            transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out; /* トランジションを追加 */
        }
        .login-input:focus {
            outline: none; /* フォーカス時のアウトラインを削除 */
            border-color: #3B82F6; /* フォーカス時のボーダー色を変更 */
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15); /* フォーカス時のシャドウを追加 */
        }

        .login-button {
            background-color: #1E3A8A;
            color: white;
            padding: 0.8rem 1.5rem; /* ボタンのパディングを調整 */
            border-radius: 0.375rem; /* 角を丸く */
            font-weight: 600;
            border: none;
            cursor: pointer;
            width: 100%; /* 幅を100%に */
            font-size: 1.1rem; /*フォントサイズを大きく */
            transition: background-color 0.2s ease-in-out, transform 0.1s ease-in-out, box-shadow 0.2s ease-in-out; /* トランジションを追加 */
            display: block; /* ブロック要素にする */
            text-align: center; /* テキストを中央揃え */
        }
        .login-button:hover {
            background-color: #172563;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .login-button:active {
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .login-help-text {
            margin-top: 1.5rem; /* マージンを調整 */
            font-size: 0.9rem; /* フォントサイズを少し小さく */
            color: #4B5563;
            text-align: center;
        }
        .login-help-link {
            color: #3B82F6;
            text-decoration: none;
            font-weight: 600;
        }
        .login-help-link:hover {
            text-decoration: underline;
        }

        .error-message {
            color: #DC2626;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            padding: 0.5rem;
            background-color: #FEE2E2;
            border-radius: 0.375rem;
            border: 1px solid #FECACA;
        }

        .app-description {
            margin-top: 2rem;
            padding: 1.25rem;
            background-color: #F3F4F6;
            border-radius: 0.5rem;
        }

        .app-description h3 {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            color: #1E3A8A;
        }

        .app-description p {
            font-size: 0.9rem;
            color: #4B5563;
            margin-bottom: 0.5rem;
            line-height: 1.5;
        }

        .app-description ul {
            list-style-position: inside;
            padding-left: 0;
            margin-bottom: 0;
        }

        .app-description li {
            font-size: 0.9rem;
            color: #4B5563;
            margin-bottom: 0.25rem;
        }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def header():
        """アプリヘッダー表示"""
        st.markdown(f'<h1 class="main-header">{Config.APP_TITLE}</h1>', unsafe_allow_html=True)

    @staticmethod
    def sidebar_navigation():
        """サイドバーナビゲーション"""
        st.sidebar.markdown('<div class="sidebar-header">メニュー</div>', unsafe_allow_html=True)
        # メニューオプション
        menu_options = {
            "ダッシュボード": "dashboard",
            "支払い処理": "payment",
            "キャッシュマネジメント": "cash_management",
            "システム設定": "system_settings",
            "エラー診断": "error_diagnostics",
            "トランザクション履歴": "transaction_history",
        }
        selected_menu = st.sidebar.radio("", list(menu_options.keys()))
        # APIサーバー設定
        st.sidebar.markdown("""---""")
        st.sidebar.markdown('<div class="sidebar-header">API接続設定</div>', unsafe_allow_html=True)
        api_base_url = st.sidebar.text_input(
            "APIサーバーURL", value=st.session_state.get("api_base_url", Config.DEFAULT_API_BASE_URL), key="api_base_url_input"
        )
        if api_base_url != st.session_state.get("api_base_url", ""):
            st.session_state.api_base_url = api_base_url
            st.sidebar.success("API接続設定が更新されました")
        # サイドバーフッター
        st.sidebar.markdown("""---""")
        if st.session_state.logged_in:
            if st.sidebar.button("ログアウト"):
                api = CashPointPayAPI(st.session_state.api_base_url)
                api.logout()
                st.session_state.logged_in = False
                st.experimental_rerun()
        return menu_options[selected_menu]

@staticmethod
def login_page():
    """ログインページ表示"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">ログイン</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        with st.form("login_form"):
            username = st.text_input("ユーザー名", key="username")
            password = st.text_input("パスワード", type="password", key="password")
            submitted = st.form_submit_button("ログイン")
            if submitted:
                if not st.session_state.get("api_base_url"):
                    st.error("APIサーバーのURLを設定してください。")
                elif not username or not password:
                    st.error("ユーザー名とパスワードを入力してください。")
                else:
                    api = CashPointPayAPI(st.session_state.api_base_url)
                    response = api.login(username, password)
                    if response.get("isSuccess", False):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success("ログインに成功しました！")
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        st.error("ログインに失敗しました。ユーザー名とパスワードを確認してください。")

    with col2:
        st.markdown("""
        <div style="padding: 1rem; background-color: #F3F4F6; border-radius: 0.5rem;">
            <h3>Cash Point Payマネジメントシステム</h3>
            <p>このシステムは、モジュールの管理・操作用UIです。</p>
            <ul>
                <li>支払い処理</li>
                <li>キャッシュ管理</li>
                <li>システム設定</li>
                <li>モニタリングとレポート</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


    @staticmethod
    def dashboard_page(api: CashPointPayAPI):
        """ダッシュボードページ表示"""
        st.markdown('<h2 class="main-header">ダッシュボード</h2>', unsafe_allow_html=True)
        # 機器情報の表示
        machine_info = api.get_machine_info()
        if machine_info.get("isSuccess", False):
            st.markdown('<div class="info-box info-box-success">', unsafe_allow_html=True)
            st.markdown(f"<strong>機器ID:</strong> {machine_info['deviceId']}", unsafe_allow_html=True)
            st.markdown(f"<strong>モデル:</strong> {machine_info['model']}", unsafe_allow_html=True)
            st.markdown(f"<strong>シリアル番号:</strong> {machine_info['serialNumber']}", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box info-box-error">機器情報の取得に失敗しました。</div>', unsafe_allow_html=True)

        # 現金情報の表示
        cash_info = api.get_cash_info()
        if cash_info.get("isSuccess", False):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">現金情報</div>', unsafe_allow_html=True)
            st.markdown(f"<strong>総現金:</strong> {cash_info['cash']}円", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box info-box-error">現金情報の取得に失敗しました。</div>', unsafe_allow_html=True)

        # その他のダッシュボード要素（必要に応じて追加）
        # 例: トランザクションの概要、エラーログの表示など

    @staticmethod
    def payment_page(api: CashPointPayAPI):
        """支払い処理ページ表示"""
        st.markdown('<h2 class="main-header">支払い処理</h2>', unsafe_allow_html=True)

        # 商品リスト入力フォーム
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">商品リスト</div>', unsafe_allow_html=True)
        items = []
        num_items = st.number_input("商品数", min_value=1, value=1, step=1)
        for i in range(num_items):
            col1, col2 = st.columns(2)
            with col1:
                item_name = st.text_input(f"商品名 {i+1}", value=f"商品{i+1}")
            with col2:
                item_price = st.number_input(f"価格 {i+1}", min_value=0, value=100, step=100)
            items.append({"name": item_name, "price": item_price})
        st.markdown('</div>', unsafe_allow_html=True)

        # 支払い実行
        if st.button("支払い実行"):
            response = api.pay(items)
            if response.get("isSuccess", False):
                st.success(f"支払い処理が開始されました。取引ID: {response.get('uuid')}")
                st.session_state.current_transaction_uuid = response.get("uuid")
            else:
                st.error("支払い処理に失敗しました。")

        # 取引照会
        if st.session_state.current_transaction_uuid:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">取引照会</div>', unsafe_allow_html=True)
            query_button = st.button("取引状況を照会")
            if query_button:
                response = api.query(st.session_state.current_transaction_uuid)
                if response.get("isSuccess", False):
                    st.success(f"取引状況: {response.get('status')}")  # statusはAPIのレスポンスに依存
                else:
                    st.error("取引状況の照会に失敗しました。")
            st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def cash_management_page(api: CashPointPayAPI):
        """キャッシュマネジメントページ表示"""
        st.markdown('<h2 class="main-header">キャッシュマネジメント</h2>', unsafe_allow_html=True)

        # 現金情報の表示
        cash_info = api.get_cash_info()
        if cash_info.get("isSuccess", False):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">現金情報</div>', unsafe_allow_html=True)
            st.markdown(f"総現金: {cash_info['cash']}円", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("現金情報の取得に失敗しました。")

        # 現金補充
        if st.button("現金補充開始"):
            response = api.refill()
            if response.get("isSuccess", False):
                st.success("現金補充プロセスを開始しました。")
            else:
                st.error("現金補充の開始に失敗しました。")

        if st.button("現金補充終了"):
            response = api.refill_end()
            if response.get("isSuccess", False):
                st.success("現金補充プロセスを終了しました。")
            else:
                st.error("現金補充の終了に失敗しました。")

        # 現金払い戻し
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">現金払い戻し</div>', unsafe_allow_html=True)
        refund_amount = st.text_input("払い戻し金額", value="0")
        if st.button("払い戻し実行"):
            response = api.refund(refund_amount)
            if response.get("isSuccess", False):
                st.success(f"{refund_amount}円の払い戻しに成功しました。")
            else:
                st.error("払い戻しに失敗しました。")
            st.markdown('</div>', unsafe_allow_html=True)

        # 現金引き出し
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">現金引き出し</div>', unsafe_allow_html=True)
        withdraw_items = []
        denominations = [10000, 5000, 2000, 1000, 500, 100, 50, 10, 5, 1]  # 紙幣と硬貨の金額
        for denomination in denominations:
            amount = st.number_input(f"{denomination}円", min_value=0, value=0, step=1)
            if amount > 0:
                withdraw_items.append({"denomination": denomination, "count": amount})
        if st.button("引き出し実行"):
            response = api.withdraw(withdraw_items)
            if response.get("isSuccess", False):
                st.success("現金の引き出しに成功しました。")
            else:
                st.error("現金の引き出しに失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def system_settings_page(api: CashPointPayAPI):
        """システム設定ページ表示"""
        st.markdown('<h2 class="main-header">システム設定</h2>', unsafe_allow_html=True)

        # デバイス設定
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">デバイス設定</div>', unsafe_allow_html=True)
        device_id = st.text_input("デバイスID")
        url = st.text_input("URL")
        if st.button("設定"):
            response = api.set_device_setting(device_id, url)
            if response.get("isSuccess", False):
                st.success("デバイス設定を保存しました。")
            else:
                st.error("デバイス設定の保存に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

        # ユーザー設定
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">ユーザー設定</div>', unsafe_allow_html=True)
        setting_name = st.text_input("設定名")
        setting_value = st.number_input("設定値", value=0)
        if st.button("設定を保存"):
            response = api.setup_setting(setting_name, setting_value)
            if response.get("isSuccess", False):
                st.success("ユーザー設定を保存しました。")
            else:
                st.error("ユーザー設定の保存に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def error_diagnostics_page(api: CashPointPayAPI):
        """エラー診断ページ表示"""
        st.markdown('<h2 class="main-header">エラー診断</h2>', unsafe_allow_html=True)

        # エラーメッセージ取得
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">エラーメッセージ取得</div>', unsafe_allow_html=True)
        error_code = st.text_input("エラーコード")
        if st.button("エラーメッセージを取得"):
            response = api.get_error_message(error_code)
            if response.get("isSuccess", False):
                st.success(f"エラーメッセージ: {response.get('message')}")  # 'message' キーはAPIのレスポンスに依存
            else:
                st.error("エラーメッセージの取得に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

        # センサー状態の取得
        if st.button("センサー状態を取得"):
            response = api.get_sensor_status()
            if response.get("isSuccess", False):
                st.json(response)  # レスポンス全体を表示。必要に応じて整形
            else:
                st.error("センサー状態の取得に失敗しました。")

        # カセット状態の取得
        if st.button("カセット状態を取得"):
            response = api.get_cassette_status()
            if response.get("isSuccess", False):
                st.json(response)
            else:
                st.error("カセット状態の取得に失敗しました。")

        # 自己診断テスト
        if st.button("自己診断テストを実行"):
            response = api.self_test()
            if response.get("isSuccess", False):
                st.success("自己診断テストが完了しました。")
                st.json(response)
            else:
                st.error("自己診断テストに失敗しました。")

    @staticmethod
    def transaction_history_page():
        """トランザクション履歴ページ表示"""
        st.markdown('<h2 class="main-header">トランザクション履歴</h2>', unsafe_allow_html=True)
        st.info("トランザクション履歴はまだ実装されていません。")  # または、データを表示するロジックをここに追加

    @staticmethod
    def footer():
        """フッター表示"""
        st.markdown('<div class="footer">© 2024 Cash Point Pay System. All rights reserved.</div>', unsafe_allow_html=True)

# メインアプリクラス
class CashPointPayApp:
    def __init__(self):
        # セッション状態の初期化
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False

        if "current_transaction_uuid" not in st.session_state:
            st.session_state.current_transaction_uuid = ""

        if "api_base_url" not in st.session_state:
            st.session_state.api_base_url = Config.DEFAULT_API_BASE_URL

        # ページ設定
        UI.set_page_config()

    def run(self):
        """アプリケーションの実行"""
        UI.header()

        # APIインスタンス
        api = CashPointPayAPI(st.session_state.api_base_url)

        if not st.session_state.logged_in:
            # 未ログイン状態
            UI.login_page()
        else:
            # ログイン済み状態
            selected_page = UI.sidebar_navigation()

            if selected_page == "dashboard":
                UI.dashboard_page(api)
            elif selected_page == "payment":
                UI.payment_page(api)
            elif selected_page == "cash_management":
                UI.cash_management_page(api)
            elif selected_page == "system_settings":
                UI.system_settings_page(api)
            elif selected_page == "error_diagnostics":
                UI.error_diagnostics_page(api)
            elif selected_page == "transaction_history":
                UI.transaction_history_page()

        UI.footer()

if __name__ == "__main__":
    app = CashPointPayApp()
    app.run()

