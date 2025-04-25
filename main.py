"""
Cash Point Pay Management System

This application provides a comprehensive interface for managing and operating
Cash Point Pay modules. It allows for payment processing, cash management,
system configuration, error diagnostics, and transaction tracking.
"""

import streamlit as st
import requests
import json
import pandas as pd
import time
import base64
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional, Union, Tuple

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

class Config:
    """Application configuration settings and constants."""
    
    # Default settings
    DEFAULT_API_BASE_URL = "http://localhost:8080"
    APP_TITLE = "Cash Point Pay マネジメントシステム"
    SESSION_COOKIE = "cash_point_pay_session"
    
    # API endpoints
    ENDPOINTS = {
        # Authentication endpoints
        "login": "/api/login",
        "logout": "/api/logOut",
        
        # Payment endpoints
        "pay": "/api/pay",
        "payment": "/api/payment",
        "pos_pay": "/api/POS/pay",
        "pos_payment": "/api/POS/payment",
        "query": "/api/query",
        
        # Machine info endpoints
        "machine_info": "/api/machineInfo",
        "door_control": "/api/doorControl",
        
        # Cash management endpoints
        "cash_info": "/api/cashInfo",
        "cash_detail_info": "/api/cashDetailInfo",
        "refill": "/api/refill",
        "refill_end": "/api/refillend",
        "refund": "/api/refund",
        "withdraw": "/api/withdraw",
        
        # Transaction control endpoints
        "cancel": "/api/cancel",
        "payment_stop": "/api/paymentStop",
        "payment_continue": "/api/paymentContinue",
        
        # Status and diagnostics endpoints
        "sensor_status": "/api/sensorStatus",
        "cassette_status": "/api/cassetteStatus",
        "get_status": "/api/getStatus",
        "reset_status": "/api/resetStatus",
        "get_error_message": "/api/getErrorMessage",
        
        # Maintenance endpoints
        "pd_calibration": "/api/pdCalibration",
        "reset_cassette": "/api/resetCassette",
        "reset_coin_box": "/api/resetCoinBox",
        "drum_to_cassette": "/api/drumToCassette",
        "self_test": "/api/selfTest",
        "clear_hopper": "/api/clearHopper",
        
        # Configuration endpoints
        "banknote_denomination_setup_get": "/api/banknoteDenominationSetup",
        "banknote_denomination_setup_post": "/api/banknoteDenominationSetup",
        "coin_tube_setup_get": "/api/coinTubeSetup",
        "coin_tube_setup_post": "/api/coinTubeSetup",
        "set_device_setting": "/api/setDeviceSetting",
        "setup_setting": "/api/setupSetting"
    }
    
    # API error codes and messages
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

# -----------------------------------------------------------------------------
# API Client
# -----------------------------------------------------------------------------

class CashPointPayAPI:
    """API client for interacting with the Cash Point Pay system."""
    
    def __init__(self, base_url: str):
        """Initialize the API client.
        
        Args:
            base_url: Base URL for the API server
        """
        self.base_url = base_url
        self.session = requests.Session()
    
    def make_url(self, endpoint: str) -> str:
        """Generate the complete URL for an API endpoint.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Complete URL for the API endpoint
        """
        return f"{self.base_url}{endpoint}"
    
    def handle_response(self, response: requests.Response) -> Dict:
        """Process API response and handle errors.
        
        Args:
            response: Response from API request
            
        Returns:
            Parsed response data
        """
        try:
            data = response.json()
            if not data.get("isSuccess", False):
                st.error(f"APIエラー: {data.get('errorMsg', '不明なエラー')}")
            return data
        except json.JSONDecodeError:
            st.error(f"応答の解析に失敗しました: {response.text}")
            return {"isSuccess": False, "errorMsg": "応答の解析に失敗しました"}
    
    # Authentication methods
    
    def login(self, account: str, password: str) -> Dict:
        """Log in to the system.
        
        Args:
            account: User account name
            password: User password
            
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["login"])
        payload = {"account": account, "password": password}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)
    
    def logout(self) -> Dict:
        """Log out from the system.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["logout"])
        response = self.session.get(url)
        return self.handle_response(response)
    
    # Payment methods
    
    def pay(self, items: List[Dict[str, Any]]) -> Dict:
        """Start payment process with items.
        
        Args:
            items: List of items to pay for
            
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["pay"])
        payload = {"items": items}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)
    
    def payment(self, amount: str) -> Dict:
        """Start payment process with specific amount.
        
        Args:
            amount: Payment amount
            
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["payment"])
        payload = {"amount": amount}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)
    
    def pos_pay(self, items: List[Dict[str, Any]], pos_reference_number: str) -> Dict:
        """Start payment process with items and POS reference.
        
        Args:
            items: List of items to pay for
            pos_reference_number: POS reference number
            
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["pos_pay"])
        payload = {"items": items, "POS_reference_number": pos_reference_number}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)
    
    def pos_payment(self, amount: str, pos_reference_number: str) -> Dict:
        """Start payment process with amount and POS reference.
        
        Args:
            amount: Payment amount
            pos_reference_number: POS reference number
            
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["pos_payment"])
        payload = {"amount": amount, "POS_reference_number": pos_reference_number}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)
    
    def query(self, uuid: str) -> Dict:
        """Query transaction status.
        
        Args:
            uuid: Transaction UUID
            
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["query"])
        payload = {"uuid": uuid}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)
    
    # Machine information methods
    
    def get_machine_info(self) -> Dict:
        """Get machine information.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["machine_info"])
        response = self.session.get(url)
        return self.handle_response(response)
    
    def door_control(self, door_settings: Dict[str, str], timeout: int = 10) -> Dict:
        """Control door locks.
        
        Args:
            door_settings: Door control settings
            timeout: Door open timeout in seconds
            
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["door_control"])
        payload = {**door_settings, "Open Timeout": timeout}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)
    
    # Cash management methods
    
    def get_cash_info(self) -> Dict:
        """Get cash information.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["cash_info"])
        response = self.session.get(url)
        return self.handle_response(response)
    
    def get_cash_detail_info(self, name: str) -> Dict:
        """Get detailed cash information for a specific drum.
        
        Args:
            name: Drum name
            
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["cash_detail_info"])
        payload = {"name": name}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)
    
    def refill(self) -> Dict:
        """Start cash module refill process.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["refill"])
        response = self.session.post(url)
        return self.handle_response(response)
    
    def refill_end(self) -> Dict:
        """End cash module refill process.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["refill_end"])
        response = self.session.post(url)
        return self.handle_response(response)
    
    def refund(self, amount: str) -> Dict:
        """Refund a specific amount.
        
        Args:
            amount: Refund amount
            
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["refund"])
        payload = {"amount": amount}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)
    
    def withdraw(self, withdraw_items: List[Dict[str, Any]]) -> Dict:
        """Withdraw specific banknotes and coins.
        
        Args:
            withdraw_items: Withdrawal specifications
            
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["withdraw"])
        payload = {"withdraw": withdraw_items}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)
    
    # Transaction control methods
    
    def cancel(self) -> Dict:
        """Cancel the current payment.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["cancel"])
        response = self.session.post(url)
        return self.handle_response(response)
    
    def payment_stop(self) -> Dict:
        """Complete the current transaction.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["payment_stop"])
        response = self.session.post(url)
        return self.handle_response(response)
    
    def payment_continue(self) -> Dict:
        """Resume a paused transaction.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["payment_continue"])
        response = self.session.post(url)
        return self.handle_response(response)
    
    # Status and diagnostic methods
    
    def get_sensor_status(self) -> Dict:
        """Get module sensor status.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["sensor_status"])
        response = self.session.get(url)
        return self.handle_response(response)
    
    def get_cassette_status(self) -> Dict:
        """Get cassette status.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["cassette_status"])
        response = self.session.get(url)
        return self.handle_response(response)
    
    def get_status(self) -> Dict:
        """Get system status.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["get_status"])
        response = self.session.get(url)
        return self.handle_response(response)
    
    def reset_status(self) -> Dict:
        """Reset device status to standby.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["reset_status"])
        response = self.session.get(url)
        return self.handle_response(response)
    
    def get_error_message(self, error_code: str) -> Dict:
        """Get error message for an error code.
        
        Args:
            error_code: Error code
            
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["get_error_message"])
        payload = {"errorCode": error_code}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)
    
    # Maintenance methods
    
    def pd_calibration(self) -> Dict:
        """Perform banknote module position detector calibration.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["pd_calibration"])
        response = self.session.post(url)
        return self.handle_response(response)
    
    def reset_cassette(self) -> Dict:
        """Reset cassette count.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["reset_cassette"])
        response = self.session.post(url)
        return self.handle_response(response)
    
    def reset_coin_box(self) -> Dict:
        """Reset coin box count.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["reset_coin_box"])
        response = self.session.post(url)
        return self.handle_response(response)
    
    def drum_to_cassette(self, drum_id: int, pcs: int) -> Dict:
        """Move banknotes from drum to cassette.
        
        Args:
            drum_id: Drum ID
            pcs: Number of pieces to move
            
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["drum_to_cassette"])
        payload = {"drumId": drum_id, "pcs": pcs}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)
    
    def self_test(self) -> Dict:
        """Run self diagnostic test on banknote and coin modules.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["self_test"])
        response = self.session.get(url)
        return self.handle_response(response)
    
    def clear_hopper(self, hopper_id: int) -> Dict:
        """Clear hopper.
        
        Args:
            hopper_id: Hopper ID
            
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["clear_hopper"])
        payload = {"hopperId": hopper_id}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)
    
    # Configuration methods
    
    def get_banknote_denomination_setup(self) -> Dict:
        """Get banknote module denomination settings.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["banknote_denomination_setup_get"])
        response = self.session.get(url)
        return self.handle_response(response)
    
    def set_banknote_denomination_setup(self, settings: List[Dict[str, Any]]) -> Dict:
        """Configure banknote module denomination settings.
        
        Args:
            settings: Banknote denomination settings
            
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["banknote_denomination_setup_post"])
        response = self.session.post(url, json=settings)
        return self.handle_response(response)
    
    def get_coin_tube_setup(self) -> Dict:
        """Get coin module settings.
        
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["coin_tube_setup_get"])
        response = self.session.get(url)
        return self.handle_response(response)
    
    def set_coin_tube_setup(self, settings: List[Dict[str, Any]]) -> Dict:
        """Configure coin module settings.
        
        Args:
            settings: Coin tube settings
            
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["coin_tube_setup_post"])
        response = self.session.post(url, json=settings)
        return self.handle_response(response)
    
    def set_device_setting(self, device_id: str, url: str) -> Dict:
        """Configure device settings.
        
        Args:
            device_id: Device ID
            url: Device URL
            
        Returns:
            API response data
        """
        url_endpoint = self.make_url(Config.ENDPOINTS["set_device_setting"])
        payload = {"deviceId": device_id, "url": url}
        response = self.session.post(url_endpoint, json=payload)
        return self.handle_response(response)
    
    def setup_setting(self, name: str, value: int) -> Dict:
        """Configure user settings.
        
        Args:
            name: Setting name
            value: Setting value
            
        Returns:
            API response data
        """
        url = self.make_url(Config.ENDPOINTS["setup_setting"])
        payload = {"name": name, "value": value}
        response = self.session.post(url, json=payload)
        return self.handle_response(response)

# -----------------------------------------------------------------------------
# UI Components
# -----------------------------------------------------------------------------

class UI:
    """UI components and page rendering."""
    
    @staticmethod
    def set_page_config():
        """Configure page settings and custom CSS."""
        st.set_page_config(
            page_title=Config.APP_TITLE,
            page_icon="💰",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
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
        """Display application header."""
        st.markdown(f'<h1 class="main-header">{Config.APP_TITLE}</h1>', unsafe_allow_html=True)
    
    @staticmethod
    def sidebar_navigation():
        """Render sidebar navigation and API settings.
        
        Returns:
            Selected page identifier
        """
        st.sidebar.markdown('<div class="sidebar-header">メニュー</div>', unsafe_allow_html=True)
        
        # Menu options
        menu_options = {
            "ダッシュボード": "dashboard",
            "支払い処理": "payment",
            "キャッシュマネジメント": "cash_management",
            "システム設定": "system_settings",
            "エラー診断": "error_diagnostics",
            "トランザクション履歴": "transaction_history",
        }
        
        selected_menu = st.sidebar.radio("", list(menu_options.keys()))
        
        # API server settings
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
        
        # Sidebar footer
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
        """Render login page."""
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
                    # Perform API login
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
        """Render dashboard page.
        
        Args:
            api: API client instance
        """
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">システム概要</div>', unsafe_allow_html=True)
        
        # System status
        UI._render_system_status(api)
        
        # Machine information
        UI._render_machine_info(api)
        
        # Cash information
        UI._render_dashboard_cash_info(api)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def _render_system_status(api: CashPointPayAPI):
        """Render system status section.
        
        Args:
            api: API client instance
        """
        status_response = api.get_status()
        
        if status_response.get("isSuccess", False):
            status_data = status_response.get("data", {})
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                banknote_connected = status_data.get("Banknote Modules Connected", False)
                banknote_status = "🟢 接続済み" if banknote_connected else "🔴 未接続"
                st.metric("紙幣モジュールステータス", banknote_status)
            
            with col2:
                coin_connected = status_data.get("Coin Modules Connected", False)
                coin_status = "🟢 接続済み" if coin_connected else "🔴 未接続"
                st.metric("硬貨モジュールステータス", coin_status)
            
            with col3:
                current_status = status_data.get("Status", "不明")
                st.metric("システムステータス", current_status)
    
    @staticmethod
    def _render_machine_info(api: CashPointPayAPI):
        """Render machine information section.
        
        Args:
            api: API client instance
        """
        machine_info_response = api.get_machine_info()
        
        if machine_info_response.get("isSuccess", False):
            machine_data = machine_info_response.get("data", {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("機器情報")
                st.write(f"マシンID: {machine_data.get('machineId', '不明')}")
                st.write(f"シリアル番号: {machine_data.get('serialNumber', '不明')}")
            
            with col2:
                st.subheader("ドアステータス")
                door_status = machine_data.get("doorStatus", [])
                
                for door in door_status:
                    status = door.get("status", "不明")
                    status_icon = "🟢" if status.lower() == "closed" else "🔴"
                    st.write(f"{status_icon} {door.get('name', '不明')}: {status}")
    
    @staticmethod
    def _render_dashboard_cash_info(api: CashPointPayAPI):
        """Render cash information section for dashboard.
        
        Args:
            api: API client instance
        """
        cash_info_response = api.get_cash_info()
        
        if cash_info_response.get("isSuccess", False):
            cash_data = cash_info_response.get("data", {})
            
            st.subheader("キャッシュ概要")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("紙幣情報")
                notes = cash_data.get("note", [])
                
                if notes:
                    note_df = pd.DataFrame(notes)
                    st.dataframe(note_df)
                    
                    # Pie chart - Banknote denomination distribution
                    valid_notes = [note for note in notes if note.get("denomination", 0) < 10000]
                    if valid_notes:
                        fig = px.pie(
                            valid_notes, 
                            values="amount", 
                            names="denomination",
                            title="紙幣の金種分布",
                            color_discrete_sequence=px.colors.sequential.Blues
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.write("硬貨情報")
                coins = cash_data.get("coin", [])
                
                if coins:
                    coin_df = pd.DataFrame(coins)
                    st.dataframe(coin_df)
                    
                    # Pie chart - Coin denomination distribution
                    valid_coins = [coin for coin in coins if coin.get("denomination", 0) > 0]
                    if valid_coins:
                        fig = px.pie(
                            valid_coins, 
                            values="amount", 
                            names="denomination",
                            title="硬貨の金種分布",
                            color_discrete_sequence=px.colors.sequential.Greens
                        )
                        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def payment_page(api: CashPointPayAPI):
        """Render payment processing page.
        
        Args:
            api: API client instance
        """
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">支払い処理</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["単一金額の支払い", "商品リストによる支払い", "POSシステム連携"])
        
        with tab1:
            UI._render_single_amount_payment(api)
        
        with tab2:
            UI._render_item_list_payment(api)
        
        with tab3:
            UI._render_pos_payment(api)
        
        # Transaction status checking section
        UI._render_transaction_status_section(api)
        
        # Transaction operation section
        UI._render_transaction_operations(api)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def _render_single_amount_payment(api: CashPointPayAPI):
        """Render single amount payment tab.
        
        Args:
            api: API client instance
        """
        st.subheader("金額指定の支払い")
        amount = st.text_input("支払い金額", key="payment_amount")
        
        if st.button("支払い処理開始", key="start_payment"):
            if amount:
                response = api.payment(amount)
                if response.get("isSuccess", False):
                    transaction_data = response.get("data", {})
                    uuid = transaction_data.get("uuid", "")
                    st.session_state.current_transaction_uuid = uuid
                    st.success(f"支払い処理が開始されました。取引ID: {uuid}")
                else:
                    st.error("支払い処理の開始に失敗しました。")
            else:
                st.warning("支払い金額を入力してください。")
    
    @staticmethod
    def _render_item_list_payment(api: CashPointPayAPI):
        """Render item list payment tab.
        
        Args:
            api: API client instance
        """
        st.subheader("商品リストによる支払い")
        
        # Dynamic item list
        if "items" not in st.session_state:
            st.session_state.items = [{"name": "", "pcs": "1", "price": ""}]
        
        for i, item in enumerate(st.session_state.items):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 0.5])
            
            with col1:
                st.session_state.items[i]["name"] = st.text_input(
                    "商品名", 
                    value=item["name"], 
                    key=f"item_name_{i}"
                )
            
            with col2:
                st.session_state.items[i]["pcs"] = st.text_input(
                    "数量", 
                    value=item["pcs"], 
                    key=f"item_pcs_{i}"
                )
            
            with col3:
                st.session_state.items[i]["price"] = st.text_input(
                    "単価", 
                    value=item["price"], 
                    key=f"item_price_{i}"
                )
            
            with col4:
                if i > 0 and st.button("削除", key=f"remove_item_{i}"):
                    st.session_state.items.pop(i)
                    st.experimental_rerun()
        
        if st.button("商品を追加"):
            st.session_state.items.append({"name": "", "pcs": "1", "price": ""})
            st.experimental_rerun()
        
        total_amount = sum(
            int(item["pcs"]) * int(item.get("price", 0)) 
            for item in st.session_state.items 
            if item.get("price", "").isdigit()
        )
        st.write(f"合計金額: {total_amount}")
        
        if st.button("支払い処理開始", key="start_pay_with_items"):
            valid_items = [item for item in st.session_state.items if item["name"] and item["pcs"] and item["price"]]
            
            if valid_items:
                response = api.pay(valid_items)
                if response.get("isSuccess", False):
                    transaction_data = response.get("data", {})
                    uuid = transaction_data.get("uuid", "")
                    st.session_state.current_transaction_uuid = uuid
                    st.success(f"支払い処理が開始されました。取引ID: {uuid}")
                else:
                    st.error("支払い処理の開始に失敗しました。")
            else:
                st.warning("少なくとも1つの有効な商品を入力してください。")
    
    @staticmethod
    def _render_pos_payment(api: CashPointPayAPI):
        """Render POS system integration tab.
        
        Args:
            api: API client instance
        """
        st.subheader("POSシステム連携")
        
        pos_tab1, pos_tab2 = st.tabs(["POSシステム - 商品リスト", "POSシステム - 金額指定"])
        
        with pos_tab1:
            UI._render_pos_item_list_payment(api)
        
        with pos_tab2:
            UI._render_pos_amount_payment(api)
    
    @staticmethod
    def _render_pos_item_list_payment(api: CashPointPayAPI):
        """Render POS item list payment subtab.
        
        Args:
            api: API client instance
        """
        st.write("POSシステム参照番号と商品リストによる支払い")
        
        pos_ref = st.text_input("POS参照番号", key="pos_ref_items")
        
        # Dynamic POS item list
        if "pos_items" not in st.session_state:
            st.session_state.pos_items = [{"name": "", "pcs": "1", "price": ""}]
        
        for i, item in enumerate(st.session_state.pos_items):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 0.5])
            
            with col1:
                st.session_state.pos_items[i]["name"] = st.text_input(
                    "商品名", 
                    value=item["name"], 
                    key=f"pos_item_name_{i}"
                )
            
            with col2:
                st.session_state.pos_items[i]["pcs"] = st.text_input(
                    "数量", 
                    value=item["pcs"], 
                    key=f"pos_item_pcs_{i}"
                )
            
            with col3:
                st.session_state.pos_items[i]["price"] = st.text_input(
                    "単価", 
                    value=item["price"], 
                    key=f"pos_item_price_{i}"
                )
            
            with col4:
                if i > 0 and st.button("削除", key=f"remove_pos_item_{i}"):
                    st.session_state.pos_items.pop(i)
                    st.experimental_rerun()
        
        if st.button("商品を追加", key="add_pos_item"):
            st.session_state.pos_items.append({"name": "", "pcs": "1", "price": ""})
            st.experimental_rerun()
        
        pos_total_amount = sum(
            int(item["pcs"]) * int(item.get("price", 0)) 
            for item in st.session_state.pos_items 
            if item.get("price", "").isdigit()
        )
        st.write(f"合計金額: {pos_total_amount}")
        
        if st.button("POS支払い処理開始", key="start_pos_pay"):
            if not pos_ref:
                st.warning("POS参照番号を入力してください。")
            else:
                valid_items = [
                    item for item in st.session_state.pos_items 
                    if item["name"] and item["pcs"] and item["price"]
                ]
                
                if valid_items:
                    response = api.pos_pay(valid_items, pos_ref)
                    if response.get("isSuccess", False):
                        transaction_data = response.get("data", {})
                        uuid = transaction_data.get("uuid", "")
                        st.session_state.current_transaction_uuid = uuid
                        st.success(f"POS支払い処理が開始されました。取引ID: {uuid}")
                    else:
                        st.error("POS支払い処理の開始に失敗しました。")
                else:
                    st.warning("少なくとも1つの有効な商品を入力してください。")
    
    @staticmethod
    def _render_pos_amount_payment(api: CashPointPayAPI):
        """Render POS amount payment subtab.
        
        Args:
            api: API client instance
        """
        st.write("POSシステム参照番号と金額による支払い")
        
        pos_ref_amount = st.text_input("POS参照番号", key="pos_ref_amount")
        pos_amount = st.text_input("支払い金額", key="pos_payment_amount")
        
        if st.button("POS金額支払い処理開始", key="start_pos_payment"):
            if not pos_ref_amount:
                st.warning("POS参照番号を入力してください。")
            elif not pos_amount:
                st.warning("支払い金額を入力してください。")
            else:
                response = api.pos_payment(pos_amount, pos_ref_amount)
                if response.get("isSuccess", False):
                    transaction_data = response.get("data", {})
                    uuid = transaction_data.get("uuid", "")
                    st.session_state.current_transaction_uuid = uuid
                    st.success(f"POS金額支払い処理が開始されました。取引ID: {uuid}")
                else:
                    st.error("POS金額支払い処理の開始に失敗しました。")
    
    @staticmethod
    def _render_transaction_status_section(api: CashPointPayAPI):
        """Render transaction status checking section.
        
        Args:
            api: API client instance
        """
        st.markdown("""---""")
        st.subheader("取引ステータス確認")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            transaction_uuid = st.text_input(
                "取引ID", 
                value=st.session_state.get("current_transaction_uuid", ""),
                key="transaction_uuid"
            )
        
        with col2:
            if st.button("ステータス確認", key="check_transaction"):
                if transaction_uuid:
                    response = api.query(transaction_uuid)
                    if response.get("isSuccess", False):
                        transaction_data = response.get("data", {})
                        
                        # Display transaction details
                        st.json(transaction_data)
                        
                        # Highlight status in info box
                        info = transaction_data.get("info", {})
                        status = info.get("status", "不明")
                        
                        status_class = "info-box-success"
                        if status in ["Payment Error", "user cancelled", "no change"]:
                            status_class = "info-box-error"
                        elif status in ["paying", "processing"]:
                            status_class = "info-box-warning"
                        
                        st.markdown(f"""
                        <div class="info-box {status_class}">
                            <strong>取引ステータス:</strong> {status}<br>
                            <strong>支払い金額:</strong> {info.get("pay_amount", 0)}<br>
                            <strong>お釣り:</strong> {info.get("change", 0)}<br>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("取引ステータスの取得に失敗しました。")
                else:
                    st.warning("取引IDを入力してください。")
    
    @staticmethod
    def _render_transaction_operations(api: CashPointPayAPI):
        """Render transaction operation section.
        
        Args:
            api: API client instance
        """
        st.markdown("""---""")
        st.subheader("取引操作")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("キャンセル", key="cancel_transaction"):
                response = api.cancel()
                if response.get("isSuccess", False):
                    st.success("取引がキャンセルされました。")
                else:
                    st.error("取引のキャンセルに失敗しました。")
        
        with col2:
            if st.button("停止", key="stop_transaction"):
                response = api.payment_stop()
                if response.get("isSuccess", False):
                    st.success("取引が停止されました。")
                else:
                    st.error("取引の停止に失敗しました。")
        
        with col3:
            if st.button("続行", key="continue_transaction"):
                response = api.payment_continue()
                if response.get("isSuccess", False):
                    st.success("取引が再開されました。")
                else:
                    st.error("取引の再開に失敗しました。")
        
        with col4:
            if st.button("リセット", key="reset_status"):
                response = api.reset_status()
                if response.get("isSuccess", False):
                    st.success("システムステータスがリセットされました。")
                else:
                    st.error("システムステータスのリセットに失敗しました。")
    
    @staticmethod
    def cash_management_page(api: CashPointPayAPI):
        """Render cash management page.
        
        Args:
            api: API client instance
        """
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">キャッシュマネジメント</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["現金情報", "補充/払い戻し", "ドラム管理", "キャッシュ操作"])
        
        with tab1:
            UI._render_cash_info_tab(api)
        
        with tab2:
            UI._render_refill_refund_tab(api)
        
        with tab3:
            UI._render_drum_management_tab(api)
        
        with tab4:
            UI._render_cash_operations_tab(api)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def _render_cash_info_tab(api: CashPointPayAPI):
        """Render cash information tab.
        
        Args:
            api: API client instance
        """
        st.subheader("現金情報")
        
        if st.button("現金情報更新", key="refresh_cash_info"):
            st.session_state.cash_info = api.get_cash_info()
        
        cash_info_response = st.session_state.get("cash_info") or api.get_cash_info()
        
        if cash_info_response.get("isSuccess", False):
            cash_data = cash_info_response.get("data", {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                UI._render_banknote_info(api, cash_data)
            
            with col2:
                UI._render_coin_info(cash_data)
        else:
            st.error("現金情報の取得に失敗しました。")
    
    @staticmethod
    def _render_banknote_info(api: CashPointPayAPI, cash_data: Dict):
        """Render banknote information.
        
        Args:
            api: API client instance
            cash_data: Cash information data
        """
        st.write("紙幣情報")
        notes = cash_data.get("note", [])
        
        if notes:
            note_df = pd.DataFrame(notes)
            
            # Total banknote amount
            total_note_amount = sum(note.get("amount", 0) for note in notes)
            st.metric("紙幣合計金額", f"{total_note_amount}")
            
            # Data table
            st.dataframe(note_df)
            
            # Detailed drum information
            st.write("ドラム詳細情報")
            selected_drum = st.selectbox(
                "ドラムを選択", 
                [note.get("name") for note in notes],
                key="selected_drum"
            )
            
            if st.button("詳細情報を表示", key="show_drum_detail"):
                drum_detail_response = api.get_cash_detail_info(selected_drum)
                if drum_detail_response.get("isSuccess", False):
                    drum_detail = drum_detail_response.get("data", {})
                    st.json(drum_detail)
                else:
                    st.error("ドラム詳細情報の取得に失敗しました。")
    
    @staticmethod
    def _render_coin_info(cash_data: Dict):
        """Render coin information.
        
        Args:
            cash_data: Cash information data
        """
        st.write("硬貨情報")
        coins = cash_data.get("coin", [])
        
        if coins:
            coin_df = pd.DataFrame(coins)
            
            # Total coin amount
            total_coin_amount = sum(coin.get("amount", 0) for coin in coins)
            st.metric("硬貨合計金額", f"{total_coin_amount}")
            
            # Data table
            st.dataframe(coin_df)
            
            # Bar chart - Coin inventory
            valid_coins = [coin for coin in coins if coin.get("denomination", 0) > 0]
            if valid_coins:
                fig = px.bar(
                    valid_coins,
                    x="denomination",
                    y="pcs",
                    color="name",
                    title="硬貨在庫状況",
                    labels={"denomination": "金種", "pcs": "枚数", "name": "場所"}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _render_refill_refund_tab(api: CashPointPayAPI):
        """Render refill/refund operations tab.
        
        Args:
            api: API client instance
        """
        st.subheader("補充/払い戻し操作")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("補充操作")
            
            if st.button("補充開始", key="start_refill"):
                response = api.refill()
                if response.get("isSuccess", False):
                    transaction_data = response.get("data", {})
                    uuid = transaction_data.get("uuid", "")
                    st.session_state.current_refill_uuid = uuid
                    st.success(f"補充プロセスが開始されました。ID: {uuid}")
                else:
                    st.error("補充プロセスの開始に失敗しました。")
            
            if st.button("補充終了", key="end_refill"):
                response = api.refill_end()
                if response.get("isSuccess", False):
                    st.success("補充プロセスが完了しました。")
                else:
                    st.error("補充プロセスの終了に失敗しました。")
        
        with col2:
            st.write("払い戻し操作")
            
            refund_amount = st.text_input("払い戻し金額", key="refund_amount")
            
            if st.button("払い戻し実行", key="execute_refund"):
                if refund_amount:
                    response = api.refund(refund_amount)
                    if response.get("isSuccess", False):
                        transaction_data = response.get("data", {})
                        uuid = transaction_data.get("uuid", "")
                        st.session_state.current_refund_uuid = uuid
                        st.success(f"払い戻しプロセスが開始されました。ID: {uuid}")
                    else:
                        st.error("払い戻しプロセスの開始に失敗しました。")
                else:
                    st.warning("払い戻し金額を入力してください。")
    
    @staticmethod
    def _render_drum_management_tab(api: CashPointPayAPI):
        """Render drum management tab.
        
        Args:
            api: API client instance
        """
        st.subheader("ドラム管理")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("ドラムからカセットへの移動")
            
            drum_id = st.number_input("ドラムID (1-4)", min_value=1, max_value=4, value=1, step=1, key="drum_id")
            drum_pcs = st.number_input("移動枚数", min_value=1, value=1, step=1, key="drum_pcs")
            
            if st.button("移動実行", key="execute_drum_to_cassette"):
                response = api.drum_to_cassette(drum_id, drum_pcs)
                if response.get("isSuccess", False):
                    st.success(f"ドラム {drum_id} からカセットに {drum_pcs} 枚の紙幣が移動されました。")
                else:
                    st.error("紙幣の移動に失敗しました。")
        
        with col2:
            st.write("カセット/コインボックスのリセット")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("カセットリセット", key="reset_cassette"):
                    response = api.reset_cassette()
                    if response.get("isSuccess", False):
                        st.success("カセットカウントがリセットされました。")
                    else:
                        st.error("カセットリセットに失敗しました。")
            
            with col2:
                if st.button("コインボックスリセット", key="reset_coin_box"):
                    response = api.reset_coin_box()
                    if response.get("isSuccess", False):
                        st.success("コインボックスカウントがリセットされました。")
                    else:
                        st.error("コインボックスリセットに失敗しました。")
    
    @staticmethod
    def _render_cash_operations_tab(api: CashPointPayAPI):
        """Render cash operations tab.
        
        Args:
            api: API client instance
        """
        st.subheader("引き出し操作")
        
        st.write("特定の紙幣・硬貨を引き出し")
        
        # Withdrawal item list
        if "withdraw_items" not in st.session_state:
            st.session_state.withdraw_items = [{"iscoin": False, "pcs": 1, "deno": 100}]
        
        for i, item in enumerate(st.session_state.withdraw_items):
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                st.session_state.withdraw_items[i]["iscoin"] = st.selectbox(
                    "種類", 
                    [("硬貨", True), ("紙幣", False)],
                    format_func=lambda x: x[0],
                    index=1 if not item["iscoin"] else 0,
                    key=f"withdraw_type_{i}"
                )[1]
            
            with col2:
                st.session_state.withdraw_items[i]["pcs"] = st.number_input(
                    "枚数", 
                    min_value=0,
                    value=item["pcs"],
                    key=f"withdraw_pcs_{i}"
                )
            
            with col3:
                denominations = [1, 5, 10, 50, 100, 500, 1000, 5000, 10000]
                st.session_state.withdraw_items[i]["deno"] = st.selectbox(
                    "金種", 
                    denominations,
                    index=denominations.index(item["deno"]) if item["deno"] in denominations else 4,
                    key=f"withdraw_deno_{i}"
                )
            
            with col4:
                if i > 0 and st.button("削除", key=f"remove_withdraw_{i}"):
                    st.session_state.withdraw_items.pop(i)
                    st.experimental_rerun()
        
        if st.button("アイテムを追加", key="add_withdraw_item"):
            st.session_state.withdraw_items.append({"iscoin": False, "pcs": 1, "deno": 100})
            st.experimental_rerun()
        
        # Calculate total amount
        total_withdraw = sum(item["pcs"] * item["deno"] for item in st.session_state.withdraw_items)
        st.write(f"合計引き出し金額: {total_withdraw}")
        
        if st.button("引き出し実行", key="execute_withdraw"):
            valid_items = [item for item in st.session_state.withdraw_items if item["pcs"] > 0]
            
            if valid_items:
                response = api.withdraw(valid_items)
                if response.get("isSuccess", False):
                    transaction_data = response.get("data", {})
                    uuid = transaction_data.get("uuid", "")
                    st.session_state.current_withdraw_uuid = uuid
                    st.success(f"引き出しプロセスが開始されました。ID: {uuid}")
                else:
                    st.error("引き出しプロセスの開始に失敗しました。")
            else:
                st.warning("少なくとも1つのアイテムの枚数を1以上に設定してください。")
    
    @staticmethod
    def system_settings_page(api: CashPointPayAPI):
        """Render system settings page.
        
        Args:
            api: API client instance
        """
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">システム設定</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["一般設定", "紙幣設定", "硬貨設定", "ドア制御", "センサー状態"])
        
        with tab1:
            UI._render_general_settings_tab(api)
        
        with tab2:
            UI._render_banknote_settings_tab(api)
        
        with tab3:
            UI._render_coin_settings_tab(api)
        
        with tab4:
            UI._render_door_control_tab(api)
        
        with tab5:
            UI._render_sensor_status_tab(api)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def _render_general_settings_tab(api: CashPointPayAPI):
        """Render general settings tab.
        
        Args:
            api: API client instance
        """
        st.subheader("一般設定")
        
        # Status operations
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("ステータスリセット", key="reset_system_status"):
                response = api.reset_status()
                if response.get("isSuccess", False):
                    st.success("システムステータスがリセットされました。")
                else:
                    st.error("システムステータスのリセットに失敗しました。")
        
        with col2:
            if st.button("自己診断テスト実行", key="run_self_test"):
                response = api.self_test()
                if response.get("isSuccess", False):
                    st.success("自己診断テストが正常に実行されました。")
                else:
                    st.error("自己診断テストの実行に失敗しました。")
        
        with col3:
            if st.button("キャリブレーション実行", key="run_calibration"):
                response = api.pd_calibration()
                if response.get("isSuccess", False):
                    st.success("紙幣モジュールのキャリブレーションが正常に実行されました。")
                else:
                    st.error("キャリブレーションの実行に失敗しました。")
        
        # Device settings
        st.markdown("""---""")
        st.write("デバイス設定")
        
        col1, col2 = st.columns(2)
        
        with col1:
            device_id = st.text_input("デバイスID", value="CPP-", key="device_id")
        
        with col2:
            device_url = st.text_input("URL", key="device_url")
        
        if st.button("デバイス設定保存", key="save_device_settings"):
            if device_id and device_url:
                response = api.set_device_setting(device_id, device_url)
                if response.get("isSuccess", False):
                    st.success("デバイス設定が保存されました。")
                else:
                    st.error("デバイス設定の保存に失敗しました。")
            else:
                st.warning("デバイスIDとURLを入力してください。")
        
        # User settings
        st.markdown("""---""")
        st.write("ユーザー設定")
        
        setting_name = st.selectbox(
            "設定名", 
            [
                "hasCoinPocketSensor", 
                "refillBanknoteByDepositMode", 
                "disablePrintReceiptForTransaction"
            ],
            key="setting_name"
        )
        
        setting_value = st.radio(
            "値", 
            [("有効", 1), ("無効", 0)],
            format_func=lambda x: x[0],
            key="setting_value"
        )[1]
        
        st.write(setting_name + "の説明:")
        if setting_name == "hasCoinPocketSensor":
            st.write("硬貨モジュールが存在する場合、この機能を有効にすると硬貨モジュールをサポートします。")
        elif setting_name == "refillBanknoteByDepositMode":
            st.write("有効にすると、補充モードでドラムに入ることができない紙幣はカセットに転送されます。無効にすると、リジェクトポケットに転送されます。")
        elif setting_name == "disablePrintReceiptForTransaction":
            st.write("トランザクション中にレシート印刷機能を無効にします。")
        
        if st.button("設定を保存", key="save_user_setting"):
            response = api.setup_setting(setting_name, setting_value)
            if response.get("isSuccess", False):
                st.success("ユーザー設定が保存されました。")
            else:
                st.error("ユーザー設定の保存に失敗しました。")
        
        # Hopper clear
        st.markdown("""---""")
        st.write("ホッパークリア")
        
        hopper_id = st.selectbox(
            "ホッパーID", 
            [("すべてのホッパー", -1), ("ホッパー1", 1), ("ホッパー2", 2), 
             ("ホッパー3", 3), ("ホッパー4", 4), ("ホッパー5", 5), ("ホッパー6", 6)],
            format_func=lambda x: x[0],
            key="hopper_id"
        )[1]
        
        if st.button("ホッパークリア実行", key="clear_hopper"):
            response = api.clear_hopper(hopper_id)
            if response.get("isSuccess", False):
                st.success(f"ホッパークリアが正常に実行されました。")
            else:
                st.error("ホッパークリアの実行に失敗しました。")
    
    @staticmethod
    def _render_banknote_settings_tab(api: CashPointPayAPI):
        """Render banknote module settings tab.
        
        Args:
            api: API client instance
        """
        st.subheader("紙幣モジュール設定")
        
        if st.button("紙幣設定読み込み", key="load_banknote_settings"):
            st.session_state.banknote_settings = api.get_banknote_denomination_setup()
        
        banknote_settings_response = st.session_state.get("banknote_settings") or api.get_banknote_denomination_setup()
        
        if banknote_settings_response.get("isSuccess", False):
            banknote_settings = banknote_settings_response.get("data", [])
            
            if banknote_settings:
                # Display current banknote settings as a table
                edited_banknote_settings = []
                
                for i, setting in enumerate(banknote_settings):
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        denomination = st.number_input(
                            f"金種 {i+1}", 
                            value=int(setting.get("denomination", 0)),
                            key=f"banknote_deno_{i}"
                        )
                    
                    with col2:
                        max_pcs = st.number_input(
                            f"最大枚数 {i+1}", 
                            value=int(setting.get("maxPcs", 0)),
                            key=f"banknote_max_pcs_{i}"
                        )
                    
                    edited_banknote_settings.append({
                        "denomination": denomination,
                        "maxPcs": max_pcs
                    })
                
                if st.button("紙幣設定を保存", key="save_banknote_settings"):
                    response = api.set_banknote_denomination_setup(edited_banknote_settings)
                    if response.get("isSuccess", False):
                        st.success("紙幣設定が保存されました。")
                    else:
                        st.error("紙幣設定の保存に失敗しました。")
            else:
                st.error("紙幣設定データが見つかりませんでした。")
        else:
            st.error("紙幣設定データの取得に失敗しました。")
    
    @staticmethod
    def _render_coin_settings_tab(api: CashPointPayAPI):
        """Render coin module settings tab.
        
        Args:
            api: API client instance
        """
        st.subheader("硬貨モジュール設定")
        
        if st.button("硬貨設定読み込み", key="load_coin_settings"):
            st.session_state.coin_settings = api.get_coin_tube_setup()
        
        coin_settings_response = st.session_state.get("coin_settings") or api.get_coin_tube_setup()
        
        if coin_settings_response.get("isSuccess", False):
            coin_settings = coin_settings_response.get("data", [])
            
            if coin_settings:
                # Display current coin settings as a table
                edited_coin_settings = []
                
                for i, setting in enumerate(coin_settings):
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col1:
                        input_enabled = st.checkbox(
                            f"入金有効 {i+1}", 
                            value=setting.get("input", True),
                            key=f"coin_input_{i}"
                        )
                    
                    with col2:
                        output_enabled = st.checkbox(
                            f"出金有効 {i+1}", 
                            value=setting.get("output", True),
                            key=f"coin_output_{i}"
                        )
                    
                    with col3:
                        pcs = st.number_input(
                            f"枚数 {i+1}", 
                            value=int(setting.get("pcs", 0)),
                            key=f"coin_pcs_{i}"
                        )
                    
                    edited_coin_settings.append({
                        "input": input_enabled,
                        "output": output_enabled,
                        "pcs": pcs
                    })
                
                if st.button("硬貨設定を保存", key="save_coin_settings"):
                    response = api.set_coin_tube_setup(edited_coin_settings)
                    if response.get("isSuccess", False):
                        st.success("硬貨設定が保存されました。")
                    else:
                        st.error("硬貨設定の保存に失敗しました。")
            else:
                st.error("硬貨設定データが見つかりませんでした。")
        else:
            st.error("硬貨設定データの取得に失敗しました。")
    
    @staticmethod
    def _render_door_control_tab(api: CashPointPayAPI):
        """Render door control tab.
        
        Args:
            api: API client instance
        """
        st.subheader("ドア制御")
        
        # Get door information
        machine_info_response = api.get_machine_info()
        
        if machine_info_response.get("isSuccess", False):
            machine_data = machine_info_response.get("data", {})
            door_status = machine_data.get("doorStatus", [])
            
            # Display current door status
            st.write("現在のドアステータス")
            
            for door in door_status:
                status = door.get("status", "不明")
                status_icon = "🟢" if status.lower() == "closed" else "🔴"
                st.write(f"{status_icon} {door.get('name', '不明')}: {status}")
            
            # Door control settings
            st.markdown("""---""")
            st.write("ドア制御設定")
            
            # Dynamically create door settings
            door_settings = {}
            
            col1, col2 = st.columns(2)
            
            with col1:
                door_settings["Note Security Door"] = st.selectbox(
                    "紙幣セキュリティドア",
                    ["open", "close"],
                    key="note_security_door"
                )
                
                door_settings["Note Drum Door"] = st.selectbox(
                    "紙幣ドラムドア",
                    ["open", "close"],
                    key="note_drum_door"
                )
                
                door_settings["Note Cassette Door"] = st.selectbox(
                    "紙幣カセットドア",
                    ["open", "close"],
                    key="note_cassette_door"
                )
            
            with col2:
                door_settings["Coin Security Door"] = st.selectbox(
                    "硬貨セキュリティドア",
                    ["open", "close"],
                    key="coin_security_door"
                )
                
                timeout = st.number_input(
                    "オープンタイムアウト（秒）",
                    min_value=1,
                    max_value=60,
                    value=10,
                    key="door_timeout"
                )
            
            if st.button("ドア制御を実行", key="execute_door_control"):
                response = api.door_control(door_settings, timeout)
                if response.get("isSuccess", False):
                    st.success("ドア制御が正常に実行されました。")
                else:
                    st.error("ドア制御の実行に失敗しました。")
        else:
            st.error("機器情報の取得に失敗しました。")
    
    @staticmethod
    def _render_sensor_status_tab(api: CashPointPayAPI):
        """Render sensor status tab.
        
        Args:
            api: API client instance
        """
        st.subheader("センサー状態")
        
        if st.button("センサー状態更新", key="refresh_sensor_status"):
            st.session_state.sensor_status = api.get_sensor_status()
        
        sensor_status_response = st.session_state.get("sensor_status") or api.get_sensor_status()
        
        if sensor_status_response.get("isSuccess", False):
            sensor_data = sensor_status_response.get("data", {})
            sensor_status = sensor_data.get("sensorStatus", {})
            
            # Banknote sensors
            st.write("紙幣センサー状態")
            note_sensors = sensor_status.get("noteSensor", [])
            
            if note_sensors:
                # Format and display sensor data
                sensor_df = pd.DataFrame(note_sensors)
                
                # Parse status column into "on/off" and "value"
                sensor_df["on_off"] = sensor_df["status"].apply(lambda x: x.split("/")[0].strip())
                sensor_df["value"] = sensor_df["status"].apply(lambda x: int(x.split("/")[1].strip()))
                
                # Display table
                st.dataframe(sensor_df)
                
                # Display heatmap
                pivot_df = sensor_df.pivot(index="name", values="value", columns=["on_off"])
                
                if not pivot_df.empty:
                    fig = px.imshow(
                        pivot_df,
                        labels=dict(x="状態", y="センサー名", color="値"),
                        title="センサー値ヒートマップ"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("紙幣センサーデータが見つかりませんでした。")
            
            # Cassette status
            st.markdown("""---""")
            st.write("カセットステータス")
            
            cassette_status_response = api.get_cassette_status()
            
            if cassette_status_response.get("isSuccess", False):
                cassette_data = cassette_status_response.get("data", {})
                cassette_status = cassette_data.get("cassetteStatus", "不明")
                
                status_icon = "🟢" if cassette_status.lower() == "true" else "🔴"
                st.write(f"{status_icon} カセットステータス: {cassette_status}")
            else:
                st.error("カセットステータスの取得に失敗しました。")
        else:
            st.error("センサー状態の取得に失敗しました。")
    
    @staticmethod
    def error_diagnostics_page(api: CashPointPayAPI):
        """Render error diagnostics page.
        
        Args:
            api: API client instance
        """
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">エラー診断</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            UI._render_error_code_search(api)
        
        with col2:
            UI._render_error_code_list(api)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def _render_error_code_search(api: CashPointPayAPI):
        """Render error code search section.
        
        Args:
            api: API client instance
        """
        st.write("エラーコード検索")
        
        error_code = st.text_input("エラーコード (例: 001001)", key="error_code")
        
        if st.button("エラーメッセージを取得", key="get_error_message"):
            if error_code:
                response = api.get_error_message(error_code)
                if response.get("isSuccess", False):
                    error_message = response.get("data", "エラーメッセージが見つかりませんでした。")
                    
                    st.markdown(f"""
                    <div class="info-box info-box-error">
                        <strong>エラーコード:</strong> {error_code}<br>
                        <strong>メッセージ:</strong> {error_message}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("エラーメッセージの取得に失敗しました。")
            else:
                st.warning("エラーコードを入力してください。")
    
    @staticmethod
    def _render_error_code_list(api: CashPointPayAPI):
        """Render error code list section.
        
        Args:
            api: API client instance
        """
        st.write("システムエラーコード一覧")
        
        # Error code table
        error_codes = {
            "001xxx": "紙幣モジュールエラー",
            "002xxx": "硬貨モジュールエラー",
            "003xxx": "システムエラー"
        }
        
        specific_errors = {
            "001001": "紙幣が入口に長時間放置されています。もう一度入れてください(1)",
            "001002": "紙幣が検出器に詰まっています。取り除いてください(2)",
            "001032": "紙幣の排出中にエラーが発生しました(32)",
            "002001": "硬貨が入口に詰まっています。取り除いてください(1)",
            "002010": "硬貨チューブが満杯です(10)",
            "003001": "システム通信エラー(1)",
            "003010": "データベースエラー(10)"
        }
        
        # Display error code classifications
        st.write("エラーコード分類")
        error_category_df = pd.DataFrame([
            {"コード範囲": code, "説明": desc} for code, desc in error_codes.items()
        ])
        st.dataframe(error_category_df)
        
        # Display specific error code examples
        st.write("代表的なエラーコード例")
        specific_error_df = pd.DataFrame([
            {"エラーコード": code, "説明": desc} for code, desc in specific_errors.items()
        ])
        st.dataframe(specific_error_df)
        
        # Get system status
        st.markdown("""---""")
        st.write("現在のシステムエラーステータス")
        
        status_response = api.get_status()
        
        if status_response.get("isSuccess", False):
            status_data = status_response.get("data", {})
            detail = status_data.get("Detail", {})
            
            note_error = detail.get("Note Error Code", 0)
            coin_error = detail.get("Coin Error Code", 0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                note_status = "🟢 正常" if note_error == 0 else f"🔴 エラー ({note_error})"
                st.metric("紙幣モジュールエラー", note_status)
            
            with col2:
                coin_status = "🟢 正常" if coin_error == 0 else f"🔴 エラー ({coin_error})"
                st.metric("硬貨モジュールエラー", coin_status)
            
            # Display details if errors are present
            if note_error != 0 or coin_error != 0:
                st.markdown(f"""
                <div class="info-box info-box-warning">
                    <strong>エラーが検出されました</strong><br>
                    ステータスをリセットするか、対応するエラーの対処方法に従ってください。
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("ステータスをリセット", key="reset_error_status"):
                    reset_response = api.reset_status()
                    if reset_response.get("isSuccess", False):
                        st.success("システムステータスがリセットされました。")
                    else:
                        st.error("システムステータスのリセットに失敗しました。")
        else:
            st.error("システムステータスの取得に失敗しました。")
    
    @staticmethod
    def transaction_history_page(api: CashPointPayAPI):
        """Render transaction history page.
        
        Args:
            api: API client instance
        """
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">トランザクション履歴</div>', unsafe_allow_html=True)
        
        # Manage UUID list
        if "transaction_history" not in st.session_state:
            st.session_state.transaction_history = []
        
        # Track new transactions
        UI._render_transaction_tracking(api)
        
        # Display history
        if st.session_state.transaction_history:
            UI._render_transaction_history()
        else:
            st.info("トランザクション履歴がありません。トランザクションIDを追加してください。")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def _render_transaction_tracking(api: CashPointPayAPI):
        """Render transaction tracking section.
        
        Args:
            api: API client instance
        """
        col1, col2 = st.columns([3, 1])
        
        with col1:
            transaction_uuid = st.text_input("トランザクションID (UUID)", key="track_uuid")
        
        with col2:
            if st.button("追跡", key="add_to_history"):
                if transaction_uuid:
                    if transaction_uuid not in [t.get("uuid") for t in st.session_state.transaction_history]:
                        response = api.query(transaction_uuid)
                        if response.get("isSuccess", False):
                            transaction_data = response.get("data", {})
                            info = transaction_data.get("info", {})
                            
                            # Add current timestamp
                            transaction_record = {
                                "uuid": transaction_uuid,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "status": info.get("status", "不明"),
                                "amount": info.get("pay_amount", 0),
                                "change": info.get("change", 0),
                                "data": transaction_data
                            }
                            
                            st.session_state.transaction_history.append(transaction_record)
                            st.success("トランザクションが履歴に追加されました。")
                        else:
                            st.error("トランザクション情報の取得に失敗しました。")
                    else:
                        st.info("このトランザクションはすでに履歴に存在します。")
                else:
                    st.warning("トランザクションIDを入力してください。")
    
    @staticmethod
    def _render_transaction_history():
        """Render transaction history display."""
        st.subheader("トランザクション履歴")
        
        # Transaction history dataframe
        history_df = pd.DataFrame([
            {
                "タイムスタンプ": record["timestamp"],
                "UUID": record["uuid"],
                "ステータス": record["status"],
                "金額": record["amount"],
                "お釣り": record["change"]
            }
            for record in st.session_state.transaction_history
        ])
        
        st.dataframe(history_df)
        
        # Transaction details display
        st.subheader("トランザクション詳細")
        
        selected_uuid = st.selectbox(
            "詳細を表示するトランザクションを選択",
            [record["uuid"] for record in st.session_state.transaction_history],
            key="selected_history_uuid"
        )
        
        selected_record = next(
            (record for record in st.session_state.transaction_history if record["uuid"] == selected_uuid),
            None
        )
        
        if selected_record:
            UI._render_transaction_details(selected_record)
        
        # Clear history
        if st.button("履歴をクリア"):
            st.session_state.transaction_history = []
            st.success("トランザクション履歴がクリアされました。")
    
    @staticmethod
    def _render_transaction_details(transaction_record: Dict):
        """Render transaction details.
        
        Args:
            transaction_record: Transaction record data
        """
        # Transaction data display
        transaction_data = transaction_record["data"]
        
        # Information section
        info = transaction_data.get("info", {})
        st.write("トランザクション情報")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("ステータス", info.get("status", "不明"))
        
        with col2:
            st.metric("支払い金額", info.get("pay_amount", 0))
        
        with col3:
            st.metric("お釣り", info.get("change", 0))
        
        # Payment items
        st.write("支払いアイテム")
        pay_items = transaction_data.get("pay", [])
        
        if pay_items:
            pay_df = pd.DataFrame(pay_items)
            st.dataframe(pay_df)
        else:
            st.info("支払いアイテムデータがありません。")
        
        # Transaction details
        st.write("取引詳細")
        detail_items = transaction_data.get("detail", [])
        
        if detail_items:
            detail_df = pd.DataFrame(detail_items)
            st.dataframe(detail_df)
            
            # Visualize transaction details
            fig = px.bar(
                detail_df,
                x="denomination",
                y="pcs",
                color="status",
                title="取引詳細グラフ",
                labels={"denomination": "金種", "pcs": "枚数", "status": "状態"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("取引詳細データがありません。")
        
        # Display JSON data
        with st.expander("トランザクションJSON全体を表示"):
            st.json(transaction_data)
    
    @
