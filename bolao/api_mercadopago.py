import mercadopago
import os


def criar_pagamento(link_pagamento):
	sdk = mercadopago.SDK(os.getenv("TOKEN_API_MERCADO_PAGO"))

	request_options = mercadopago.config.RequestOptions()
	request_options.custom_headers = {
		'x-idempotency-key': 'P7tqL'
	}

	payment_data = {
		"items": [
			{
				"id": "1234",
				"title": "Bolão Virtual",
				"description": "Pagamento da inscrição do Bolão Virtual",
				"quantity": 1,
				"currency_id": "BRL",
				"unit_price": 30,
			},
		],
  		"auto_return":"all",
		"payment_methods": {
            "excluded_payment_types": [
                {"id": "ticket"},  # Exclui boleto bancário, por exemplo
                {"id": "atm"}      # Exclui transferências bancárias
            ],
            "installments": 3,  # Limita o número máximo de parcelas no cartão
            # "default_payment_method_id": "pix"  # Pode definir Pix como opção padrão
        },
  		"back_urls": {
			"success": link_pagamento,
			"pending": link_pagamento,
			"failure": link_pagamento,
		}
	}
	result = sdk.preference().create(payment_data, request_options)
	link = result["response"]["init_point"]
	id_pagamento = result["response"]["id"]
	return link, id_pagamento
