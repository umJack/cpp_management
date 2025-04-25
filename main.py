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
        .btn-secondary {
            background-color: #6B7280;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            font-weight: 600;
            border: none;
            cursor: pointer;
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
        .btn-danger {
            background-color: #EF4444;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            font-weight: 600;
            border: none;
            cursor: pointer;
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
            "APIサーバーURL",
            value=st.session_state.get("api_base_url", Config.DEFAULT_API_BASE_URL),
            key="api_base_url_input"
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
            username = st.text_input("ユーザー名", key="username")
            password = st.text_input("パスワード", type="password", key="password")
            login_button = st.button("ログイン")
            if login_button:
                if not st.session_state.get("api_base_url"):
                    st.error("APIサーバーのURLを設定してください。")
                elif not username or not password:
                    st.error("ユーザー名とパスワードを入力してください。")
                else:
                    # 実際のAPIログイン
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
                <p>このシステムは、Cash Point Payモジュールの管理および操作のための包括的なインターフェースを提供します。</p>
                <p>以下の操作が可能です：</p>
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
        st.markdown('<div class="info-box info-box-success">ようこそ、Cash Point Payマネジメントシステムへ！</div>', unsafe_allow_html=True)

        # 機器情報の表示
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">機器情報</div>', unsafe_allow_html=True)
        machine_info = api.get_machine_info()
        if machine_info and machine_info["isSuccess"]:
            info = machine_info["data"]
            st.write(f"機器ID: {info['deviceId']}")
            st.write(f"モデル: {info['model']}")
            st.write(f"シリアル番号: {info['serialNumber']}")
            st.write(f"ソフトウェアバージョン: {info['softwareVersion']}")
            st.write(f"ハードウェアバージョン: {info['hardwareVersion']}")
        else:
            st.error("機器情報の取得に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

        # 現金情報の表示
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">現金情報</div>', unsafe_allow_html=True)
        cash_info = api.get_cash_info()
        if cash_info and cash_info["isSuccess"]:
            total_cash = cash_info["data"]["totalCash"]
            st.write(f"現在の現金総額: {total_cash}円")

            # ドラムごとの現金情報を表示
            st.markdown("<h4>ドラム別現金情報</h4>", unsafe_allow_html=True)
            for drum in cash_info["data"]["drums"]:
                st.write(f"  {drum['name']}: {drum['amount']}円")
        else:
            st.error("現金情報の取得に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

        # センサー情報の表示
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">センサー情報</div>', unsafe_allow_html=True)
        sensor_status = api.get_sensor_status()
        if sensor_status and sensor_status["isSuccess"]:
            status = sensor_status["data"]
            st.write(f"フロントドアセンサー: {'開' if status['frontDoorSensor'] else '閉'}")
            st.write(f"リアドアセンサー: {'開' if status['rearDoorSensor'] else '閉'}")
            st.write(f"侵入センサー: {'検知' if status['intrusionSensor'] else '正常'}")
            st.write(f"紙幣センサー: {'OK' if status['banknoteSensor'] else '異常'}")
            st.write(f"硬貨センサー: {'OK' if status['coinSensor'] else '異常'}")
        else:
            st.error("センサー情報の取得に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def payment_page(api: CashPointPayAPI):
        """支払い処理ページ表示"""
        st.markdown('<h2 class="main-header">支払い処理</h2>', unsafe_allow_html=True)

        # 支払い方法選択
        payment_method = st.radio("支払い方法を選択してください", ["商品指定支払い", "金額指定支払い", "POS連携支払い", "POS金額指定支払い"])

        if payment_method == "商品指定支払い":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">商品指定支払い</div>', unsafe_allow_html=True)
            items = []
            num_items = st.number_input("商品点数", min_value=1, value=1)
            for i in range(num_items):
                item_name = st.text_input(f"商品名 {i + 1}")
                item_price = st.number_input(f"価格 {i + 1}", min_value=0, value=100)
                item_quantity = st.number_input(f"数量 {i + 1}", min_value=1, value=1)
                items.append({"name": item_name, "price": item_price, "quantity": item_quantity})
            if st.button("支払う"):
                response = api.pay(items)
                if response and response["isSuccess"]:
                    st.success(f"支払い処理が開始されました。取引ID: {response['data']['uuid']}")
                    st.session_state.current_transaction_uuid = response['data']['uuid']
                else:
                    st.error("支払い処理に失敗しました。")
            st.markdown('</div>', unsafe_allow_html=True)

        elif payment_method == "金額指定支払い":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">金額指定支払い</div>', unsafe_allow_html=True)
            amount = st.text_input("金額 (円)")
            if st.button("支払う"):
                response = api.payment(amount)
                if response and response["isSuccess"]:
                    st.success(f"支払い処理が開始されました。取引ID: {response['data']['uuid']}")
                    st.session_state.current_transaction_uuid = response['data']['uuid']
                else:
                    st.error("支払い処理に失敗しました。")
            st.markdown('</div>', unsafe_allow_html=True)

        elif payment_method == "POS連携支払い":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">POS連携支払い</div>', unsafe_allow_html=True)
            pos_reference_number = st.text_input("POS参照番号")
            items = []
            num_items = st.number_input("商品点数", min_value=1, value=1)
            for i in range(num_items):
                item_name = st.text_input(f"商品名 {i + 1}")
                item_price = st.number_input(f"価格 {i + 1}", min_value=0, value=100)
                item_quantity = st.number_input(f"数量 {i + 1}", min_value=1, value=1)
                items.append({"name": item_name, "price": item_price, "quantity": item_quantity})
            if st.button("支払う"):
                response = api.pos_pay(items, pos_reference_number)
                if response and response["isSuccess"]:
                    st.success(f"支払い処理が開始されました。取引ID: {response['data']['uuid']}")
                    st.session_state.current_transaction_uuid = response['data']['uuid']
                else:
                    st.error("支払い処理に失敗しました。")
            st.markdown('</div>', unsafe_allow_html=True)

        elif payment_method == "POS金額指定支払い":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">POS金額指定支払い</div>', unsafe_allow_html=True)
            amount = st.text_input("金額 (円)")
            pos_reference_number = st.text_input("POS参照番号")
            if st.button("支払う"):
                response = api.pos_payment(amount, pos_reference_number)
                if response and response["isSuccess"]:
                    st.success(f"支払い処理が開始されました。取引ID: {response['data']['uuid']}")
                    st.session_state.current_transaction_uuid = response['data']['uuid']
                else:
                    st.error("支払い処理に失敗しました。")
            st.markdown('</div>', unsafe_allow_html=True)

        # 共通のトランザクション管理機能
        if st.session_state.current_transaction_uuid:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">トランザクション管理</div>', unsafe_allow_html=True)
            st.write(f"現在の取引ID: {st.session_state.current_transaction_uuid}")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("取引照会"):
                    response = api.query(st.session_state.current_transaction_uuid)
                    if response and response["isSuccess"]:
                        status = response["data"]["status"]
                        st.success(f"取引状況: {status}")
                    else:
                        st.error("取引照会に失敗しました。")
            with col2:
                if st.button("取引キャンセル"):
                    response = api.cancel()
                    if response and response["isSuccess"]:
                        st.success("取引がキャンセルされました。")
                        st.session_state.current_transaction_uuid = ""
                    else:
                        st.error("取引キャンセルに失敗しました。")
            with col3:
                if st.button("返金"):
                    amount = st.text_input("返金額 (円)")
                    if amount:
                        response = api.refund(amount)
                        if response and response["isSuccess"]:
                            st.success("返金処理が完了しました。")
                        else:
                            st.error("返金処理に失敗しました。")
            st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def cash_management_page(api: CashPointPayAPI):
        """キャッシュマネジメントページ表示"""
        st.markdown('<h2 class="main-header">キャッシュマネジメント</h2>', unsafe_allow_html=True)

        # 現金情報の表示
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">現金情報</div>', unsafe_allow_html=True)
        cash_info = api.get_cash_info()
        if cash_info and cash_info["isSuccess"]:
            total_cash = cash_info["data"]["totalCash"]
            st.write(f"現在の現金総額: {total_cash}円")
            # ドラムごとの現金情報を表示
            st.markdown("<h4>ドラム別現金情報</h4>", unsafe_allow_html=True)
            for drum in cash_info["data"]["drums"]:
                st.write(f"  {drum['name']}: {drum['amount']}円")
        else:
            st.error("現金情報の取得に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

        # 現金補充
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">現金補充</div>', unsafe_allow_html=True)
        if st.button("補充開始"):
            response = api.refill()
            if response and response["isSuccess"]:
                st.success("補充プロセスを開始しました。")
            else:
                st.error("補充開始に失敗しました。")
        if st.button("補充終了"):
            response = api.refill_end()
            if response and response["isSuccess"]:
                st.success("補充プロセスを終了しました。")
            else:
                st.error("補充終了に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

        # 現金引き出し
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">現金引き出し</div>', unsafe_allow_html=True)
        withdraw_items = []
        num_withdraw_items = st.number_input("引き出す紙幣・硬貨の種類", min_value=1, value=1)
        for i in range(num_withdraw_items):
            item_name = st.text_input(f"紙幣・硬貨の種類 {i + 1} (例: 1000円札, 100円玉)")
            item_quantity = st.number_input(f"枚数/個数 {i + 1}", min_value=1, value=1)
            withdraw_items.append({"name": item_name, "count": item_quantity})
        if st.button("引き出し実行"):
            response = api.withdraw(withdraw_items)
            if response and response["isSuccess"]:
                st.success("引き出し処理を開始しました。")
            else:
                st.error("引き出し処理に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

        # ドラムからカセットへの移動
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">ドラムからカセットへの移動</div>', unsafe_allow_html=True)
        drum_id = st.number_input("ドラムID (1〜4)", min_value=1, max_value=4, value=1)
        pcs = st.number_input("枚数", min_value=1, value=1)
        if st.button("移動実行"):
            response = api.drum_to_cassette(drum_id, pcs)
            if response and response["isSuccess"]:
                st.success("移動処理を開始しました。")
            else:
                st.error("移動処理に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

        # カセット関連の操作
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">カセット操作</div>', unsafe_allow_html=True)
        if st.button("カセットリセット"):
            response = api.reset_cassette()
            if response and response["isSuccess"]:
                st.success("カセットのカウントをリセットしました。")
            else:
                st.error("カセットのリセットに失敗しました。")
        if st.button("コインボックスリセット"):
            response = api.reset_coin_box()
            if response and response["isSuccess"]:
                st.success("コインボックスのカウントをリセットしました。")
            else:
                st.error("コインボックスのリセットに失敗しました。")
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
            if response and response["isSuccess"]:
                st.success("デバイス設定を更新しました。")
            else:
                st.error("デバイス設定の更新に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

        # 紙幣額面設定
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">紙幣額面設定</div>', unsafe_allow_html=True)
        banknote_settings = []
        num_banknote_types = st.number_input("紙幣の種類", min_value=1, value=1)
        for i in range(num_banknote_types):
            denomination = st.number_input(f"額面 {i + 1}", min_value=1, value=1000)
            count = st.number_input(f"枚数 {i + 1}", min_value=0, value=100)
            banknote_settings.append({"denomination": denomination, "count": count})
        if st.button("設定"):
            response = api.set_banknote_denomination_setup(banknote_settings)
            if response and response["isSuccess"]:
                st.success("紙幣額面設定を更新しました。")
            else:
                st.error("紙幣額面設定の更新に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

        # 硬貨設定
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">硬貨設定</div>', unsafe_allow_html=True)
        coin_settings = []
        num_coin_types = st.number_input("硬貨の種類", min_value=1, value=1)
        for i in range(num_coin_types):
            denomination = st.number_input(f"額面 {i + 1}", min_value=1, value=1)
            count = st.number_input(f"個数 {i + 1}", min_value=0, value=100)
            coin_settings.append({"denomination": denomination, "count": count})
        if st.button("設定"):
            response = api.set_coin_tube_setup(coin_settings)
            if response and response["isSuccess"]:
                st.success("硬貨設定を更新しました。")
            else:
                st.error("硬貨設定の更新に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

        # ユーザー設定
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">ユーザー設定</div>', unsafe_allow_html=True)
        name = st.text_input("設定名")
        value = st.number_input("設定値", value=0)
        if st.button("設定"):
            response = api.setup_setting(name, value)
            if response and response["isSuccess"]:
                st.success("ユーザー設定を更新しました。")
            else:
                st.error("ユーザー設定の更新に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def error_diagnostics_page(api: CashPointPayAPI):
        """エラー診断ページ表示"""
        st.markdown('<h2 class="main-header">エラー診断</h2>', unsafe_allow_html=True)

        # エラーメッセージ取得
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">エラーメッセージ取得</div>', unsafe_allow_html=True)
        error_code = st.text_input("エラーコード")
        if st.button("取得"):
            response = api.get_error_message(error_code)
            if response and response["isSuccess"]:
                st.success(f"エラーメッセージ: {response['data']['message']}")
            else:
                st.error("エラーメッセージの取得に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

        # セルフテスト
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">セルフテスト</div>', unsafe_allow_html=True)
        if st.button("実行"):
            response = api.self_test()
            if response and response["isSuccess"]:
                st.success("セルフテストが完了しました。")
            else:
                st.error("セルフテストに失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

        # センサー状態
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">センサー状態</div>', unsafe_allow_html=True)
        sensor_status = api.get_sensor_status()
        if sensor_status and sensor_status["isSuccess"]:
            status = sensor_status["data"]
            st.write(f"フロントドアセンサー: {'開' if status['frontDoorSensor'] else '閉'}")
            st.write(f"リアドアセンサー: {'開' if status['rearDoorSensor'] else '閉'}")
            st.write(f"侵入センサー: {'検知' if status['intrusionSensor'] else '正常'}")
            st.write(f"紙幣センサー: {'OK' if status['banknoteSensor'] else '異常'}")
            st.write(f"硬貨センサー: {'OK' if status['coinSensor'] else '異常'}")
        else:
            st.error("センサー情報の取得に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

        # カセット状態
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">カセット状態</div>', unsafe_allow_html=True)
        cassette_status = api.get_cassette_status()
        if cassette_status and cassette_status["isSuccess"]:
            status = cassette_status["data"]
            for cassette in status:
                st.write(f"{cassette['name']}:")
                st.write(f"  状態: {cassette['status']}")
                st.write(f"  在高: {cassette['count']}")
        else:
            st.error("カセット情報の取得に失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

        # PDキャリブレーション
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">PDキャリブレーション</div>', unsafe_allow_html=True)
        if st.button("実行"):
            response = api.pd_calibration()
            if response and response["isSuccess"]:
                st.success("PDキャリブレーションが完了しました。")
            else:
                st.error("PDキャリブレーションに失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

        # ホッパークリア
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">ホッパークリア</div>', unsafe_allow_html=True)
        hopper_id = st.number_input("ホッパーID", min_value=1, value=1)
        if st.button("クリア"):
            response = api.clear_hopper(hopper_id)
            if response and response["isSuccess"]:
                st.success("ホッパーをクリアしました。")
            else:
                st.error("ホッパーのクリアに失敗しました。")
        st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def transaction_history_page(api: CashPointPayAPI):
        """トランザクション履歴ページ表示"""
        st.markdown('<h2 class="main-header">トランザクション履歴</h2>', unsafe_allow_html=True)
        st.write("トランザクション履歴はまだ実装されていません。")

    @staticmethod
    def footer():
        """フッター表示"""
        st.markdown('<div class="footer">© 2024 Cash Point Pay. All rights reserved.</div>', unsafe_allow_html=True)

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
                UI.transaction_history_page(api)

        UI.footer()

if __name__ == "__main__":
    app = CashPointPayApp()
    app.run()
