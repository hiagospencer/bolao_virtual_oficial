import mercadopago


def criar_pagamento(valor,link_pagamento):
	sdk = mercadopago.SDK("TEST-266656323447145-110719-a59531039b6a8f24597978bfc17a9381-162532150")

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
				"unit_price": float(valor),
			},
		],
  		"auto_return":"all",
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
