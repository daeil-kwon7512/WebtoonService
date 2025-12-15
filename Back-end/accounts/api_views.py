from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken # [추가] 토큰 생성용
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, SurveyInputSerializer

# [내 정보 조회]
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

# [회원가입]
@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    """
    회원가입 + 자동 로그인 (토큰 발급)
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # [추가됨] 회원가입 성공 시 토큰 즉시 발급
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': '회원가입 및 로그인 성공',
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token), # Access Token
            'refresh': str(refresh),             # Refresh Token
        }, status=status.HTTP_201_CREATED)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# [설문조사 결과 제출] (NEW)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def survey_submit_view(request):
    """
    설문조사 데이터를 받아 저장하고 onboarding_completed를 True로 변경
    """
    serializer = SurveyInputSerializer(data=request.data)
    if serializer.is_valid():
        try:
            serializer.save(user=request.user)
            return Response({"message": "설문 저장 완료", "user_status": "active"}, status=status.HTTP_200_OK)
        except Exception as e:
            # 디버깅을 위해 에러 메시지 출력
            print(e)
            return Response({"error": "저장 중 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
