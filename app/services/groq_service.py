from typing import Optional
from groq import Groq
from fastapi import HTTPException
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)


class GroqService:
    def __init__(self):
        """Initialize Groq client with API key from settings"""
        try:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            self.model = settings.GROQ_MODEL
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise HTTPException(status_code=500, detail="AI service initialization failed")

    def generate_ticket_response(self, title: str, description: str) -> str:
        """
        Generate an automatic response for a support ticket using Groq AI
        
        Args:
            title: The ticket title
            description: The ticket description
            
        Returns:
            AI generated response as string
        """
        try:
            # Create a comprehensive prompt for the AI
            prompt = self._build_support_prompt(title, description)
            print(prompt)
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente de suporte técnico especializado. "
                                 "Responda de forma profissional, clara e útil em português brasileiro. "
                                 "Forneça soluções práticas e, quando necessário, sugira próximos passos."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False
            )
            
            response = chat_completion.choices[0].message.content

            print (response)
            if not response or response.strip() == "":
                return self._get_fallback_response()
                
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            # Return a fallback response instead of failing
            return self._get_fallback_response()

    def _build_support_prompt(self, title: str, description: str) -> str:
        """Build a comprehensive prompt for the AI support agent"""
        return f"""
Analise o seguinte ticket de suporte e forneça uma resposta útil e profissional:

**TÍTULO:** {title}

**DESCRIÇÃO:** {description}

Por favor, forneça:
1. Uma análise do problema reportado
2. Possíveis soluções ou passos para resolver
3. Informações adicionais que podem ser úteis
4. Se necessário, sugira quando escalar para suporte humano

Mantenha a resposta concisa mas completa, e use um tom profissional e empático.
"""

    def _get_fallback_response(self) -> str:
        """Return a fallback response when AI generation fails"""
        return """Obrigado por entrar em contato conosco. 

Recebemos seu ticket e nossa equipe está analisando sua solicitação. Retornaremos com uma resposta personalizada em breve.

Enquanto isso, você pode:
- Verificar nossa base de conhecimento para soluções rápidas
- Entrar em contato pelo chat se for urgente
- Aguardar o retorno de nossa equipe de suporte

Agradecemos sua paciência!"""

    def health_check(self) -> bool:
        """Check if the Groq service is healthy and accessible"""
        try:
            # Simple test call to verify API connectivity
            test_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model=self.model,
                max_tokens=10
            )
            return bool(test_completion.choices[0].message.content)
        except Exception as e:
            logger.error(f"Groq health check failed: {e}")
            return False

