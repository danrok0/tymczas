"""
Zaawansowany system finansowy dla City Builder
Implementuje pożyczki, raporty finansowe, analizy i prognozy
"""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import random
import math
from datetime import datetime, timedelta

class LoanType(Enum):
    STANDARD = "standard"
    EMERGENCY = "emergency"
    DEVELOPMENT = "development"
    INFRASTRUCTURE = "infrastructure"

class CreditRating(Enum):
    EXCELLENT = "excellent"  # AAA
    GOOD = "good"           # AA
    FAIR = "fair"           # A
    POOR = "poor"           # BBB
    BAD = "bad"             # BB and below

@dataclass
class Loan:
    """Reprezentuje pożyczkę"""
    id: str
    loan_type: LoanType
    principal_amount: float
    interest_rate: float
    remaining_amount: float
    monthly_payment: float
    turns_remaining: int
    taken_turn: int
    credit_rating_at_time: CreditRating
    collateral: Optional[str] = None
    
    def calculate_total_interest(self) -> float:
        """Oblicza całkowite odsetki do zapłacenia"""
        total_payments = self.monthly_payment * (self.turns_remaining + 1)
        return total_payments - self.principal_amount

class FinancialReport:
    """Raport finansowy"""
    
    def __init__(self, turn: int, data: Dict):
        self.turn = turn
        self.timestamp = datetime.now()
        self.income = data.get('income', 0)
        self.expenses = data.get('expenses', 0)
        self.net_income = self.income - self.expenses
        self.assets = data.get('assets', 0)
        self.liabilities = data.get('liabilities', 0)
        self.equity = self.assets - self.liabilities
        self.cash_flow = data.get('cash_flow', 0)
        self.debt_to_equity_ratio = self.liabilities / max(self.equity, 1)
        self.liquidity_ratio = data.get('cash', 0) / max(self.expenses, 1)

class FinanceManager:
    """Zaawansowany menedżer finansów"""
    
    def __init__(self):
        self.active_loans: List[Loan] = []
        self.loan_history: List[Loan] = []
        self.financial_reports: List[FinancialReport] = []
        self.credit_rating = CreditRating.GOOD
        self.credit_score = 750  # 300-850 scale
        self.bankruptcy_risk = 0.0  # 0-1 scale
        
        # Ustawienia pożyczek
        self.base_interest_rates = {
            LoanType.STANDARD: 0.05,      # 5%
            LoanType.EMERGENCY: 0.12,     # 12%
            LoanType.DEVELOPMENT: 0.07,   # 7%
            LoanType.INFRASTRUCTURE: 0.04  # 4%
        }
        
        # Limity pożyczek
        self.loan_limits = {
            LoanType.STANDARD: 50000,
            LoanType.EMERGENCY: 20000,
            LoanType.DEVELOPMENT: 100000,
            LoanType.INFRASTRUCTURE: 200000
        }
    
    def calculate_credit_score(self, economy, population_manager) -> int:
        """Oblicza ocenę kredytową miasta"""
        score = 750  # Bazowa ocena
        
        # Czynniki pozytywne
        money = economy.get_resource_amount('money')
        if money > 50000:
            score += min(100, money // 1000)
        
        # Populacja i zadowolenie
        total_pop = population_manager.get_total_population()
        satisfaction = population_manager.get_average_satisfaction()
        score += min(50, total_pop // 100)
        score += min(50, (satisfaction - 50) * 2)
        
        # Historia spłat
        if self.loan_history:
            paid_on_time = sum(1 for loan in self.loan_history if loan.remaining_amount == 0)
            payment_ratio = paid_on_time / len(self.loan_history)
            score += int(payment_ratio * 100)
        
        # Czynniki negatywne
        total_debt = sum(loan.remaining_amount for loan in self.active_loans)
        if total_debt > money:
            score -= min(200, (total_debt - money) // 1000)
        
        # Liczba aktywnych pożyczek
        if len(self.active_loans) > 3:
            score -= (len(self.active_loans) - 3) * 25
        
        self.credit_score = max(300, min(850, score))
        self._update_credit_rating()
        return self.credit_score
    
    def _update_credit_rating(self):
        """Aktualizuje rating kredytowy na podstawie score"""
        if self.credit_score >= 800:
            self.credit_rating = CreditRating.EXCELLENT
        elif self.credit_score >= 720:
            self.credit_rating = CreditRating.GOOD
        elif self.credit_score >= 650:
            self.credit_rating = CreditRating.FAIR
        elif self.credit_score >= 580:
            self.credit_rating = CreditRating.POOR
        else:
            self.credit_rating = CreditRating.BAD
    
    def get_loan_offer(self, loan_type: LoanType, amount: float, 
                      economy, population_manager) -> Optional[Dict]:
        """Generuje ofertę pożyczki"""
        
        # Sprawdź czy można udzielić pożyczki
        if amount > self.loan_limits[loan_type]:
            return None
        
        # Oblicz aktualną ocenę kredytową
        self.calculate_credit_score(economy, population_manager)
        
        # Sprawdź czy rating pozwala na pożyczkę
        if self.credit_rating == CreditRating.BAD and loan_type != LoanType.EMERGENCY:
            return None
        
        # Oblicz oprocentowanie
        base_rate = self.base_interest_rates[loan_type]
        
        # Modyfikatory oprocentowania
        rating_modifier = {
            CreditRating.EXCELLENT: -0.01,
            CreditRating.GOOD: 0.0,
            CreditRating.FAIR: 0.01,
            CreditRating.POOR: 0.02,
            CreditRating.BAD: 0.05
        }
        
        interest_rate = base_rate + rating_modifier[self.credit_rating]
        
        # Dodatkowe ryzyko za liczbę aktywnych pożyczek
        if len(self.active_loans) > 1:
            interest_rate += (len(self.active_loans) - 1) * 0.005
        
        # Oblicz spłatę
        if loan_type == LoanType.EMERGENCY:
            duration_turns = 24  # 2 lata
        elif loan_type == LoanType.STANDARD:
            duration_turns = 60  # 5 lat
        elif loan_type == LoanType.DEVELOPMENT:
            duration_turns = 120  # 10 lat
        else:  # INFRASTRUCTURE
            duration_turns = 180  # 15 lat
        
        monthly_payment = self._calculate_monthly_payment(amount, interest_rate, duration_turns)
        
        return {
            'loan_type': loan_type,
            'amount': amount,
            'interest_rate': interest_rate,
            'monthly_payment': monthly_payment,
            'duration_turns': duration_turns,
            'total_cost': monthly_payment * duration_turns,
            'total_interest': (monthly_payment * duration_turns) - amount,
            'credit_rating': self.credit_rating,
            'approval_chance': self._calculate_approval_chance()
        }
    
    def _calculate_monthly_payment(self, principal: float, annual_rate: float, turns: int) -> float:
        """Oblicza miesięczną spłatę pożyczki"""
        if annual_rate == 0:
            return principal / turns
        
        monthly_rate = annual_rate / 12
        return principal * (monthly_rate * (1 + monthly_rate) ** turns) / ((1 + monthly_rate) ** turns - 1)
    
    def _calculate_approval_chance(self) -> float:
        """Oblicza szansę na zatwierdzenie pożyczki"""
        base_chance = {
            CreditRating.EXCELLENT: 0.95,
            CreditRating.GOOD: 0.85,
            CreditRating.FAIR: 0.70,
            CreditRating.POOR: 0.45,
            CreditRating.BAD: 0.20
        }
        
        chance = base_chance[self.credit_rating]
        
        # Zmniejsz szansę za każdą aktywną pożyczkę
        chance -= len(self.active_loans) * 0.1
        
        return max(0.1, min(0.95, chance))
    
    def take_loan(self, loan_offer: Dict, turn: int) -> Tuple[bool, str]:
        """Zaciąga pożyczkę"""
        approval_chance = loan_offer['approval_chance']
        
        if random.random() > approval_chance:
            return False, "Wniosek o pożyczkę został odrzucony"
        
        loan = Loan(
            id=f"loan_{turn}_{len(self.active_loans)}",
            loan_type=loan_offer['loan_type'],
            principal_amount=loan_offer['amount'],
            interest_rate=loan_offer['interest_rate'],
            remaining_amount=loan_offer['amount'],
            monthly_payment=loan_offer['monthly_payment'],
            turns_remaining=loan_offer['duration_turns'],
            taken_turn=turn,
            credit_rating_at_time=self.credit_rating
        )
        
        self.active_loans.append(loan)
        return True, f"Pożyczka na kwotę ${loan_offer['amount']:,.0f} została zatwierdzona"
    
    def process_loan_payments(self, economy, turn: int) -> Dict:
        """Przetwarza spłaty pożyczek"""
        total_payment = 0
        completed_loans = []
        payment_details = []
        
        for loan in self.active_loans:
            if loan.turns_remaining > 0:
                # Sprawdź czy można dokonać spłaty
                if economy.can_afford(loan.monthly_payment):
                    economy.spend_money(loan.monthly_payment)
                    
                    # Oblicz część kapitałową i odsetkową
                    interest_portion = loan.remaining_amount * (loan.interest_rate / 12)
                    principal_portion = loan.monthly_payment - interest_portion
                    
                    loan.remaining_amount -= principal_portion
                    loan.turns_remaining -= 1
                    total_payment += loan.monthly_payment
                    
                    payment_details.append({
                        'loan_id': loan.id,
                        'payment': loan.monthly_payment,
                        'principal': principal_portion,
                        'interest': interest_portion,
                        'remaining': loan.remaining_amount
                    })
                    
                    if loan.turns_remaining == 0:
                        completed_loans.append(loan)
                        self.loan_history.append(loan)
                else:
                    # Brak środków na spłatę - kara
                    self.credit_score -= 10
                    payment_details.append({
                        'loan_id': loan.id,
                        'payment': 0,
                        'missed': True,
                        'penalty': loan.monthly_payment * 0.05
                    })
        
        # Usuń spłacone pożyczki
        for loan in completed_loans:
            self.active_loans.remove(loan)
        
        return {
            'total_payment': total_payment,
            'completed_loans': len(completed_loans),
            'payment_details': payment_details,
            'active_loans_count': len(self.active_loans)
        }
    
    def generate_financial_report(self, turn: int, economy, population_manager, 
                                buildings: List) -> FinancialReport:
        """Generuje raport finansowy"""
        
        # Oblicz aktywa
        money = economy.get_resource_amount('money')
        building_value = sum(getattr(building, 'cost', 0) * 0.8 for building in buildings)  # 80% wartości
        total_assets = money + building_value
        
        # Oblicz zobowiązania
        total_liabilities = sum(loan.remaining_amount for loan in self.active_loans)
        
        # Oblicz dochody i wydatki
        income = economy.calculate_taxes(buildings, population_manager)
        expenses = economy.calculate_expenses(buildings, population_manager)
        loan_payments = sum(loan.monthly_payment for loan in self.active_loans)
        total_expenses = expenses + loan_payments
        
        report_data = {
            'income': income,
            'expenses': total_expenses,
            'assets': total_assets,
            'liabilities': total_liabilities,
            'cash': money,
            'cash_flow': income - total_expenses
        }
        
        report = FinancialReport(turn, report_data)
        self.financial_reports.append(report)
        
        # Zachowaj tylko ostatnie 100 raportów
        if len(self.financial_reports) > 100:
            self.financial_reports.pop(0)
        
        return report
    
    def calculate_bankruptcy_risk(self, economy) -> float:
        """Oblicza ryzyko bankructwa"""
        money = economy.get_resource_amount('money')
        total_debt = sum(loan.remaining_amount for loan in self.active_loans)
        monthly_obligations = sum(loan.monthly_payment for loan in self.active_loans)
        
        risk_factors = []
        
        # Czynnik 1: Stosunek długu do gotówki
        if money > 0:
            debt_to_cash = total_debt / money
            risk_factors.append(min(1.0, debt_to_cash / 5))  # Ryzyko rośnie gdy dług > 5x gotówka
        else:
            risk_factors.append(1.0)
        
        # Czynnik 2: Zdolność do spłaty miesięcznych zobowiązań
        if money > 0:
            months_coverage = money / max(monthly_obligations, 1)
            risk_factors.append(max(0, 1 - months_coverage / 6))  # Ryzyko gdy < 6 miesięcy pokrycia
        else:
            risk_factors.append(1.0)
        
        # Czynnik 3: Trend finansowy
        if len(self.financial_reports) >= 3:
            recent_reports = self.financial_reports[-3:]
            cash_flow_trend = [r.cash_flow for r in recent_reports]
            if all(cf < 0 for cf in cash_flow_trend):
                risk_factors.append(0.8)  # Wysokie ryzyko przy ciągłych stratach
            elif cash_flow_trend[-1] < cash_flow_trend[0]:
                risk_factors.append(0.4)  # Średnie ryzyko przy pogarszającym się trendzie
            else:
                risk_factors.append(0.1)  # Niskie ryzyko przy poprawie
        
        # Czynnik 4: Rating kredytowy
        rating_risk = {
            CreditRating.EXCELLENT: 0.05,
            CreditRating.GOOD: 0.1,
            CreditRating.FAIR: 0.2,
            CreditRating.POOR: 0.4,
            CreditRating.BAD: 0.7
        }
        risk_factors.append(rating_risk[self.credit_rating])
        
        # Oblicz średnie ważone ryzyko
        self.bankruptcy_risk = sum(risk_factors) / len(risk_factors)
        return self.bankruptcy_risk
    
    def get_financial_advice(self, economy, population_manager) -> List[str]:
        """Generuje porady finansowe"""
        advice = []
        
        money = economy.get_resource_amount('money')
        total_debt = sum(loan.remaining_amount for loan in self.active_loans)
        monthly_obligations = sum(loan.monthly_payment for loan in self.active_loans)
        
        # Analiza gotówki
        if money < monthly_obligations * 3:
            advice.append("⚠️ Niski poziom gotówki. Rozważ zwiększenie podatków lub ograniczenie wydatków.")
        
        # Analiza zadłużenia
        if total_debt > money * 2:
            advice.append("💳 Wysokie zadłużenie. Skup się na spłacie pożyczek przed nowymi inwestycjami.")
        
        # Analiza ratingu
        if self.credit_rating in [CreditRating.POOR, CreditRating.BAD]:
            advice.append("📉 Niski rating kredytowy. Popraw sytuację finansową przed zaciąganiem nowych pożyczek.")
        
        # Analiza trendów
        if len(self.financial_reports) >= 5:
            recent_cash_flows = [r.cash_flow for r in self.financial_reports[-5:]]
            if all(cf < 0 for cf in recent_cash_flows):
                advice.append("📊 Ciągłe straty. Przeanalizuj źródła dochodów i koszty.")
        
        # Pozytywne porady
        if self.credit_rating == CreditRating.EXCELLENT and money > 100000:
            advice.append("✅ Doskonała sytuacja finansowa. Rozważ inwestycje rozwojowe.")
        
        if not self.active_loans and money > 50000:
            advice.append("💰 Brak zadłużenia i dobra sytuacja finansowa. Czas na ekspansję!")
        
        return advice if advice else ["✅ Sytuacja finansowa jest stabilna."]
    
    def export_financial_data(self) -> Dict:
        """Eksportuje dane finansowe do analizy"""
        return {
            'credit_score': self.credit_score,
            'credit_rating': self.credit_rating.value,
            'bankruptcy_risk': self.bankruptcy_risk,
            'active_loans': [{
                'id': loan.id,
                'type': loan.loan_type.value,
                'amount': loan.principal_amount,
                'remaining': loan.remaining_amount,
                'payment': loan.monthly_payment,
                'turns_left': loan.turns_remaining,
                'interest_rate': loan.interest_rate
            } for loan in self.active_loans],
            'financial_history': [{
                'turn': report.turn,
                'income': report.income,
                'expenses': report.expenses,
                'net_income': report.net_income,
                'assets': report.assets,
                'liabilities': report.liabilities,
                'cash_flow': report.cash_flow
            } for report in self.financial_reports[-20:]]  # Ostatnie 20 raportów
        }
    
    def save_to_dict(self) -> Dict:
        """Zapisuje stan do słownika"""
        return {
            'credit_score': self.credit_score,
            'credit_rating': self.credit_rating.value,
            'bankruptcy_risk': self.bankruptcy_risk,
            'active_loans': [{
                'id': loan.id,
                'loan_type': loan.loan_type.value,
                'principal_amount': loan.principal_amount,
                'interest_rate': loan.interest_rate,
                'remaining_amount': loan.remaining_amount,
                'monthly_payment': loan.monthly_payment,
                'turns_remaining': loan.turns_remaining,
                'taken_turn': loan.taken_turn,
                'credit_rating_at_time': loan.credit_rating_at_time.value
            } for loan in self.active_loans]
        }
    
    def load_from_dict(self, data: Dict):
        """Wczytuje stan ze słownika"""
        self.credit_score = data.get('credit_score', 750)
        self.credit_rating = CreditRating(data.get('credit_rating', 'good'))
        self.bankruptcy_risk = data.get('bankruptcy_risk', 0.0)
        
        # Wczytaj pożyczki
        self.active_loans = []
        for loan_data in data.get('active_loans', []):
            loan = Loan(
                id=loan_data['id'],
                loan_type=LoanType(loan_data['loan_type']),
                principal_amount=loan_data['principal_amount'],
                interest_rate=loan_data['interest_rate'],
                remaining_amount=loan_data['remaining_amount'],
                monthly_payment=loan_data['monthly_payment'],
                turns_remaining=loan_data['turns_remaining'],
                taken_turn=loan_data['taken_turn'],
                credit_rating_at_time=CreditRating(loan_data['credit_rating_at_time'])
            )
            self.active_loans.append(loan) 