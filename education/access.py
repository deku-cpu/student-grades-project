import json
from functools import wraps

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.views.decorators.csrf import ensure_csrf_cookie

from .choices import UserRole


def user_role(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return UserRole.ADMIN
    profile = getattr(user, 'profile', None)
    return profile.role if profile else None


def can_manage(user):
    return user_role(user) in (UserRole.ADMIN, UserRole.DEANS_OFFICE)


def check_teaching(user, teaching):
    if can_manage(user):
        return
    if user_role(user) != UserRole.TEACHER or teaching.teacher.user_id != user.pk:
        raise PermissionDenied('Нет доступа к этому журналу')


def error_response(message, status=400):
    return JsonResponse({'error': message}, status=status,
                        json_dumps_params={'ensure_ascii': False})


def read_json(request):
    data = json.loads(request.body)
    if not isinstance(data, dict):
        raise ValidationError('Ожидается JSON-объект')
    return data


def save_checked(obj):
    obj.full_clean()
    obj.save()
    return obj


def api_access(*roles, methods=('GET',)):
    # Транзакция откатывает изменения, если проверка данных завершилась ошибкой.
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.method not in methods:
                response = error_response('Метод не поддерживается', 405)
                response['Allow'] = ', '.join(methods)
                return response
            if roles:
                if not request.user.is_authenticated:
                    return error_response('Не авторизован', 401)
                if user_role(request.user) not in roles and user_role(request.user) != UserRole.ADMIN:
                    return error_response('Доступ ограничен', 403)
            actor = request.user if request.user.is_authenticated else None
            try:
                with transaction.atomic():
                    response = view(request, *args, **kwargs)
                    if 200 <= response.status_code < 300 and request.method in ('POST', 'PUT', 'DELETE'):
                        from .models import AuditLog
                        actor = request.user if request.user.is_authenticated else actor
                        action = {'POST': 'Создание', 'PUT': 'Изменение', 'DELETE': 'Удаление'}[request.method]
                        if view.__name__ == 'login_api':
                            action = 'Вход'
                        elif view.__name__ == 'logout_api':
                            action = 'Выход'
                        elif view.__name__ == 'backup_api':
                            action = 'Резервная копия'
                        AuditLog.objects.create(user=actor, action=action, path=request.path)
                    return response
            except PermissionDenied as exc:
                return error_response(str(exc) or 'Доступ ограничен', 403)
            except ProtectedError:
                return error_response('Удаление невозможно: запись используется в учебном процессе')
            except ObjectDoesNotExist:
                return error_response('Запись не найдена', 404)
            except ValidationError as exc:
                return error_response('; '.join(exc.messages))
            except (ValueError, TypeError, KeyError, OverflowError):
                return error_response('Проверьте обязательные поля и формат данных')
            except IntegrityError:
                return error_response('Такая запись уже существует или нарушает связи данных')
        return wrapped
    return decorator


def page_access(*roles):
    def decorator(view):
        @wraps(view)
        @ensure_csrf_cookie
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login_page')
            if user_role(request.user) not in roles and user_role(request.user) != UserRole.ADMIN:
                return HttpResponseForbidden('Доступ ограничен')
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


def csrf_failure(request, reason=''):
    if request.path.startswith('/api/'):
        return error_response('Защитный токен устарел. Обновите страницу и повторите действие', 403)
    return HttpResponseForbidden('Обновите страницу и повторите действие')
