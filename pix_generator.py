#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import qrcode
from io import BytesIO
import base64

def calculate_crc16(payload):
    """Calcula o CRC16 CCITT para o payload PIX (implementação corrigida)"""
    def crc16_ccitt(data):
        crc = 0xFFFF
        for byte in data.encode('utf-8'):
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
                crc &= 0xFFFF
        return crc
    
    return crc16_ccitt(payload)

def format_cpf(cpf):
    """Formata CPF removendo caracteres especiais"""
    return ''.join(filter(str.isdigit, cpf))

def generate_pix_payload(cpf, amount, description="Presente de Casamento", merchant_name="Lista de Presentes", merchant_city="SAO PAULO"):
    """
    Gera o payload PIX conforme especificação do Banco Central (versão corrigida)
    """
    cpf_formatted = format_cpf(cpf)
    
    # Payload Format Indicator
    payload = "00020"
    
    # Point of Initiation Method (static)
    payload += "126"
    
    # Merchant Account Information (PIX)
    # GUI (Globally Unique Identifier)
    gui = "0014BR.GOV.BCB.PIX"
    
    # Chave PIX (CPF)
    key_field = f"01{len(cpf_formatted):02d}{cpf_formatted}"
    
    # Descrição (opcional)
    desc_field = ""
    if description:
        description_clean = description[:25]  # Máximo 25 caracteres
        desc_field = f"02{len(description_clean):02d}{description_clean}"
    
    merchant_info = gui + key_field + desc_field
    payload += f"{len(merchant_info):02d}{merchant_info}"
    
    # Merchant Category Code
    payload += "52040000"
    
    # Transaction Currency (BRL)
    payload += "5303986"
    
    # Transaction Amount
    if amount > 0:
        amount_str = f"{amount:.2f}"
        payload += f"54{len(amount_str):02d}{amount_str}"
    
    # Country Code
    payload += "5802BR"
    
    # Merchant Name
    merchant_name_clean = merchant_name[:25]
    payload += f"59{len(merchant_name_clean):02d}{merchant_name_clean}"
    
    # Merchant City
    merchant_city_clean = merchant_city[:15]
    payload += f"60{len(merchant_city_clean):02d}{merchant_city_clean}"
    
    # Additional Data Field Template (opcional)
    additional_data = "0503***"  # Reference Label
    payload += f"62{len(additional_data):02d}{additional_data}"
    
    # CRC16
    payload += "6304"
    crc = calculate_crc16(payload)
    payload += f"{crc:04X}"
    
    return payload

def generate_qr_code_base64(payload):
    """Gera QR Code em base64 a partir do payload PIX"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converter para base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def generate_pix_data(cpf, amount, item_name):
    """Gera dados completos do PIX (payload e QR code)"""
    payload = generate_pix_payload(cpf, amount, item_name)
    qr_base64 = generate_qr_code_base64(payload)
    
    return {
        'payload': payload,
        'qr_code': qr_base64,
        'amount': amount,
        'cpf': cpf,
        'item_name': item_name
    }

if __name__ == "__main__":
    # Teste
    cpf = "13113497663"
    amount = 250.00
    item_name = "Air Fryer"
    
    pix_data = generate_pix_data(cpf, amount, item_name)
    print(f"Payload PIX: {pix_data['payload']}")
    print(f"QR Code gerado com sucesso!")

