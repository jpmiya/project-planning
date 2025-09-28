def procesar_etapas(request):
    etapas_dict = {}
    
    for key, value in request.POST.items():
        if key.startswith('etapas['):
            parts = key[7:-1].split('][')
            if len(parts) == 2:
                nombre_etapa, campo = parts
                
                if nombre_etapa not in etapas_dict:
                    etapas_dict[nombre_etapa] = {}
                
                etapas_dict[nombre_etapa][campo] = value
    
    return etapas_dict