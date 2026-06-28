import React, { useState, useEffect, useCallback } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStatus, useOnboarding } from '../hooks/useAuth';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { apiClient } from '../services/api/client';
import '../styles/pages.css';

interface RecipeDetail {
  id: string;
  title: string;
  ingredients?: string;
  instructions?: string;
  prepTimeMin?: number;
  cookTimeMin?: number;
  servings?: number;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
}

interface WeekMeal {
  id: string;
  recipeId?: string;
  mealType: string;
  title: string;
  image: string;
  calories: number;
  protein: number;
  approved: boolean;
}

interface DayPlan {
  day: string;
  totalCalories: number;
  collapsed: boolean;
  meals: WeekMeal[];
}

const REPLACEMENT_POOL: WeekMeal[] = [
  { id: 'rp1', mealType: 'BREAKFAST', title: 'Veggie Scrambled Eggs', image: 'https://images.unsplash.com/photo-1510693206972-df098062cb71?w=200&h=200&fit=crop', calories: 290, protein: 22, approved: false },
  { id: 'rp2', mealType: 'BREAKFAST', title: 'Protein Smoothie Bowl', image: 'https://images.unsplash.com/photo-1590080876614-be9c29b29330?w=200&h=200&fit=crop', calories: 380, protein: 28, approved: false },
  { id: 'rp3', mealType: 'BREAKFAST', title: 'Whole Wheat Pancakes', image: 'https://images.unsplash.com/photo-1528207776546-365bb710ee93?w=200&h=200&fit=crop', calories: 410, protein: 12, approved: false },
  { id: 'rp4', mealType: 'BREAKFAST', title: 'Greek Yogurt Parfait', image: 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=200&h=200&fit=crop', calories: 300, protein: 24, approved: false },
  { id: 'rp5', mealType: 'BREAKFAST', title: 'Avocado Toast', image: 'https://images.unsplash.com/photo-1541519227354-08fa5d50c820?w=200&h=200&fit=crop', calories: 350, protein: 14, approved: false },
  { id: 'rp6', mealType: 'LUNCH - MAIN', title: 'Mediterranean Bowl', image: 'https://images.unsplash.com/photo-1540914124281-342587941389?w=200&h=200&fit=crop', calories: 490, protein: 35, approved: false },
  { id: 'rp7', mealType: 'LUNCH - MAIN', title: 'Turkey & Veggie Wrap', image: 'https://images.unsplash.com/photo-1550304943-4f24f54ddde9?w=200&h=200&fit=crop', calories: 380, protein: 32, approved: false },
  { id: 'rp8', mealType: 'LUNCH - MAIN', title: 'Lentil Soup', image: 'https://images.unsplash.com/photo-1547592180-85f173990554?w=200&h=200&fit=crop', calories: 320, protein: 18, approved: false },
  { id: 'rp9', mealType: 'LUNCH - MAIN', title: 'Tuna Salad Bowl', image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=200&h=200&fit=crop', calories: 410, protein: 38, approved: false },
  { id: 'rp10', mealType: 'LUNCH - SIDE', title: 'Mixed Green Salad', image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=200&h=200&fit=crop', calories: 90, protein: 3, approved: false },
  { id: 'rp11', mealType: 'LUNCH - SIDE', title: 'Roasted Sweet Potato', image: 'https://images.unsplash.com/photo-1518843875459-f738682238a6?w=200&h=200&fit=crop', calories: 160, protein: 3, approved: false },
  { id: 'rp12', mealType: 'LUNCH - SIDE', title: 'Cucumber Sticks & Hummus', image: 'https://images.unsplash.com/photo-1563379926898-05f4575a45d8?w=200&h=200&fit=crop', calories: 110, protein: 5, approved: false },
  { id: 'rp13', mealType: 'DINNER - MAIN', title: 'Grilled Salmon & Veggies', image: 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=200&h=200&fit=crop', calories: 510, protein: 42, approved: false },
  { id: 'rp14', mealType: 'DINNER - MAIN', title: 'Chicken Tikka Masala', image: 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=200&h=200&fit=crop', calories: 480, protein: 38, approved: false },
  { id: 'rp15', mealType: 'DINNER - MAIN', title: 'Shrimp Stir-Fry', image: 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=200&h=200&fit=crop', calories: 390, protein: 34, approved: false },
  { id: 'rp16', mealType: 'DINNER - SIDE', title: 'Steamed Asparagus', image: 'https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=200&h=200&fit=crop', calories: 60, protein: 4, approved: false },
  { id: 'rp17', mealType: 'DINNER - SIDE', title: 'Brown Rice', image: 'https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?w=200&h=200&fit=crop', calories: 130, protein: 3, approved: false },
];

const ALL_BREAKFASTS: Omit<WeekMeal, 'id' | 'approved'>[] = [
  { mealType: 'BREAKFAST', title: 'Overnight Oats with Berries', image: 'https://images.unsplash.com/photo-1517673132405-a56a62b18caf?w=200&h=200&fit=crop', calories: 340, protein: 12 },
  { mealType: 'BREAKFAST', title: 'Veggie Scrambled Eggs', image: 'https://images.unsplash.com/photo-1510693206972-df098062cb71?w=200&h=200&fit=crop', calories: 290, protein: 22 },
  { mealType: 'BREAKFAST', title: 'Protein Smoothie Bowl', image: 'https://images.unsplash.com/photo-1590080876614-be9c29b29330?w=200&h=200&fit=crop', calories: 380, protein: 28 },
  { mealType: 'BREAKFAST', title: 'Greek Yogurt Parfait', image: 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=200&h=200&fit=crop', calories: 300, protein: 24 },
  { mealType: 'BREAKFAST', title: 'Whole Wheat Pancakes', image: 'https://images.unsplash.com/photo-1528207776546-365bb710ee93?w=200&h=200&fit=crop', calories: 410, protein: 12 },
  { mealType: 'BREAKFAST', title: 'Avocado Toast', image: 'https://images.unsplash.com/photo-1541519227354-08fa5d50c820?w=200&h=200&fit=crop', calories: 350, protein: 14 },
  { mealType: 'BREAKFAST', title: 'Chia Pudding with Mango', image: 'https://images.unsplash.com/photo-1590080874088-eec64895b423?w=200&h=200&fit=crop', calories: 310, protein: 10 },
  { mealType: 'BREAKFAST', title: 'Banana Oat Smoothie', image: 'https://images.unsplash.com/photo-1638176066666-ffb2f013c7dd?w=200&h=200&fit=crop', calories: 260, protein: 9 },
];

const ALL_LUNCH_MAINS: Omit<WeekMeal, 'id' | 'approved'>[] = [
  { mealType: 'LUNCH - MAIN', title: 'Grilled Chicken with Quinoa', image: 'https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=200&h=200&fit=crop', calories: 450, protein: 45 },
  { mealType: 'LUNCH - MAIN', title: 'Salmon Buddha Bowl', image: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=200&h=200&fit=crop', calories: 520, protein: 38 },
  { mealType: 'LUNCH - MAIN', title: 'Lean Beef Stir-Fry', image: 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=200&h=200&fit=crop', calories: 480, protein: 40 },
  { mealType: 'LUNCH - MAIN', title: 'Mediterranean Bowl', image: 'https://images.unsplash.com/photo-1540914124281-342587941389?w=200&h=200&fit=crop', calories: 490, protein: 35 },
  { mealType: 'LUNCH - MAIN', title: 'Turkey & Veggie Wrap', image: 'https://images.unsplash.com/photo-1550304943-4f24f54ddde9?w=200&h=200&fit=crop', calories: 380, protein: 32 },
  { mealType: 'LUNCH - MAIN', title: 'Lentil Soup', image: 'https://images.unsplash.com/photo-1547592180-85f173990554?w=200&h=200&fit=crop', calories: 320, protein: 18 },
  { mealType: 'LUNCH - MAIN', title: 'Tuna Salad Bowl', image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=200&h=200&fit=crop', calories: 410, protein: 38 },
  { mealType: 'LUNCH - MAIN', title: 'Falafel Wrap', image: 'https://images.unsplash.com/photo-1529042410759-befb1204b468?w=200&h=200&fit=crop', calories: 440, protein: 20 },
];

const ALL_LUNCH_SIDES: Omit<WeekMeal, 'id' | 'approved'>[] = [
  { mealType: 'LUNCH - SIDE', title: 'Mixed Green Salad', image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=200&h=200&fit=crop', calories: 90, protein: 3 },
  { mealType: 'LUNCH - SIDE', title: 'Roasted Seasonal Vegetables', image: 'https://images.unsplash.com/photo-1518843875459-f738682238a6?w=200&h=200&fit=crop', calories: 150, protein: 4 },
  { mealType: 'LUNCH - SIDE', title: 'Steamed Broccoli & Almonds', image: 'https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=200&h=200&fit=crop', calories: 140, protein: 7 },
  { mealType: 'LUNCH - SIDE', title: 'Cucumber Sticks & Hummus', image: 'https://images.unsplash.com/photo-1563379926898-05f4575a45d8?w=200&h=200&fit=crop', calories: 110, protein: 5 },
  { mealType: 'LUNCH - SIDE', title: 'Roasted Sweet Potato', image: 'https://images.unsplash.com/photo-1518843875459-f738682238a6?w=200&h=200&fit=crop', calories: 160, protein: 3 },
  { mealType: 'LUNCH - SIDE', title: 'Corn & Bean Salsa', image: 'https://images.unsplash.com/photo-1541519227354-08fa5d50c820?w=200&h=200&fit=crop', calories: 120, protein: 5 },
];

const ALL_DINNER_MAINS: Omit<WeekMeal, 'id' | 'approved'>[] = [
  { mealType: 'DINNER - MAIN', title: 'Whole Wheat Veggie Pasta', image: 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=200&h=200&fit=crop', calories: 430, protein: 18 },
  { mealType: 'DINNER - MAIN', title: 'Turkey Meatball Bowl', image: 'https://images.unsplash.com/photo-1529042410759-befb1204b468?w=200&h=200&fit=crop', calories: 460, protein: 36 },
  { mealType: 'DINNER - MAIN', title: 'Baked Cod with Herbs', image: 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=200&h=200&fit=crop', calories: 520, protein: 44 },
  { mealType: 'DINNER - MAIN', title: 'Chicken Tikka Masala', image: 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=200&h=200&fit=crop', calories: 480, protein: 38 },
  { mealType: 'DINNER - MAIN', title: 'Grilled Salmon & Veggies', image: 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=200&h=200&fit=crop', calories: 510, protein: 42 },
  { mealType: 'DINNER - MAIN', title: 'Shrimp Stir-Fry', image: 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=200&h=200&fit=crop', calories: 390, protein: 34 },
  { mealType: 'DINNER - MAIN', title: 'Beef & Veggie Stew', image: 'https://images.unsplash.com/photo-1547592180-85f173990554?w=200&h=200&fit=crop', calories: 540, protein: 42 },
  { mealType: 'DINNER - MAIN', title: 'Tofu & Veggie Curry', image: 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=200&h=200&fit=crop', calories: 410, protein: 22 },
];

const ALL_DINNER_SIDES: Omit<WeekMeal, 'id' | 'approved'>[] = [
  { mealType: 'DINNER - SIDE', title: 'Steamed Broccoli', image: 'https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=200&h=200&fit=crop', calories: 80, protein: 5 },
  { mealType: 'DINNER - SIDE', title: 'Brown Rice', image: 'https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?w=200&h=200&fit=crop', calories: 130, protein: 3 },
  { mealType: 'DINNER - SIDE', title: 'Roasted Sweet Potato', image: 'https://images.unsplash.com/photo-1518843875459-f738682238a6?w=200&h=200&fit=crop', calories: 160, protein: 3 },
  { mealType: 'DINNER - SIDE', title: 'Steamed Asparagus', image: 'https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=200&h=200&fit=crop', calories: 60, protein: 4 },
  { mealType: 'DINNER - SIDE', title: 'Garlic Sautéed Spinach', image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=200&h=200&fit=crop', calories: 70, protein: 4 },
  { mealType: 'DINNER - SIDE', title: 'Quinoa Pilaf', image: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=200&h=200&fit=crop', calories: 150, protein: 6 },
];

const pickUnique = <T,>(arr: T[], count: number): T[] => {
  const shuffled = [...arr].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, Math.min(count, shuffled.length));
};

const generateWeeklyPlan = (): DayPlan[] => {
  const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  const breakfasts = pickUnique(ALL_BREAKFASTS, 7);
  const lunchMains = pickUnique(ALL_LUNCH_MAINS, 7);
  const lunchSides = pickUnique(ALL_LUNCH_SIDES, 7);
  const dinnerMains = pickUnique(ALL_DINNER_MAINS, 7);
  const dinnerSides = pickUnique(ALL_DINNER_SIDES, 7);

  return DAYS.map((day, i) => {
    const meals: WeekMeal[] = [
      { id: `${day}-1`, ...breakfasts[i % breakfasts.length], approved: false },
      { id: `${day}-2`, ...lunchMains[i % lunchMains.length], approved: false },
      { id: `${day}-3`, ...lunchSides[i % lunchSides.length], approved: false },
      { id: `${day}-4`, ...dinnerMains[i % dinnerMains.length], approved: false },
      { id: `${day}-5`, ...dinnerSides[i % dinnerSides.length], approved: false },
    ];
    const totalCalories = meals.reduce((sum, m) => sum + m.calories, 0);
    return { day, totalCalories, collapsed: false, meals };
  });
};

export const DashboardPage: React.FC = () => {
  const { isAuthenticated, user, isLoading: authLoading } = useAuthStatus();
  const { needsOnboarding } = useOnboarding();
  const [weeklyPlan, setWeeklyPlan] = useState<DayPlan[] | null>(null);
  const [replacingMeal, setReplacingMeal] = useState<{ dayIndex: number; mealIndex: number } | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [recipeDetail, setRecipeDetail] = useState<RecipeDetail | null>(null);
  const [recipeLoading, setRecipeLoading] = useState(false);

  const handleOpenRecipe = useCallback(async (recipeId?: string) => {
    if (!recipeId) return;
    setRecipeLoading(true);
    setRecipeDetail(null);
    const res = await apiClient.get<RecipeDetail>(`/meals/recipe/${recipeId}`);
    if (res.success && res.data) setRecipeDetail(res.data);
    setRecipeLoading(false);
  }, []);

  if (!isAuthenticated && !authLoading) {
    return <Navigate to="/login" replace />;
  }

  if (needsOnboarding && !authLoading) {
    return <Navigate to="/onboarding" replace />;
  }

  if (authLoading) {
    return <LoadingSpinner message="Loading..." />;
  }

  const fetchPlanFromBackend = async () => {
    setIsGenerating(true);
    try {
      const response = await apiClient.get<any>('/meals/weekly-plan');
      if (response.success && response.data?.days?.length) {
        const days: DayPlan[] = response.data.days.map((day: any) => {
          const m = day.meals;
          const toMeal = (slot: any, slotId: string, mealType: string): WeekMeal | null =>
            slot ? { id: `${day.id}-${slotId}`, recipeId: slot.id, mealType, title: slot.title, image: slot.image, calories: slot.calories, protein: slot.protein, approved: false } : null;
          const meals: WeekMeal[] = [
            toMeal(m.breakfast,  '1', 'BREAKFAST'),
            toMeal(m.lunchMain,  '2', 'LUNCH - MAIN'),
            toMeal(m.lunchSide,  '3', 'LUNCH - SIDE'),
            toMeal(m.dinnerMain, '4', 'DINNER - MAIN'),
            toMeal(m.dinnerSide, '5', 'DINNER - SIDE'),
            toMeal(m.snack,      '6', 'SNACK'),
          ].filter(Boolean) as WeekMeal[];
          const totalCalories = meals.reduce((sum, meal) => sum + meal.calories, 0);
          return { day: day.dayName, totalCalories, collapsed: false, meals };
        });
        setWeeklyPlan(days);
      } else {
        // Fallback to mock if backend fails
        setWeeklyPlan(generateWeeklyPlan());
      }
    } catch {
      setWeeklyPlan(generateWeeklyPlan());
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerate = () => {
    fetchPlanFromBackend();
  };

  const handleRegenerate = () => {
    fetchPlanFromBackend();
  };

  const handleApprove = (dayIndex: number, mealIndex: number) => {
    setWeeklyPlan((prev) => {
      if (!prev) return prev;
      const updated = prev.map((day, di) => {
        if (di !== dayIndex) return day;
        return {
          ...day,
          meals: day.meals.map((meal, mi) =>
            mi === mealIndex ? { ...meal, approved: !meal.approved } : meal
          ),
        };
      });
      return updated;
    });
  };

  const handleToggleCollapse = (dayIndex: number) => {
    setWeeklyPlan((prev) => {
      if (!prev) return prev;
      return prev.map((day, di) =>
        di === dayIndex ? { ...day, collapsed: !day.collapsed } : day
      );
    });
  };

  const handleOpenReplace = (dayIndex: number, mealIndex: number) => {
    setReplacingMeal({ dayIndex, mealIndex });
  };

  const handleSelectReplacement = (replacement: Omit<WeekMeal, 'id' | 'approved'>) => {
    if (!replacingMeal) return;
    const { dayIndex, mealIndex } = replacingMeal;
    setWeeklyPlan((prev) => {
      if (!prev) return prev;
      return prev.map((day, di) => {
        if (di !== dayIndex) return day;
        const oldCal = day.meals[mealIndex].calories;
        const newMeals = day.meals.map((meal, mi) =>
          mi === mealIndex
            ? { ...replacement, id: meal.id, mealType: meal.mealType, approved: false }
            : meal
        );
        const diff = replacement.calories - oldCal;
        return { ...day, meals: newMeals, totalCalories: day.totalCalories + diff };
      });
    });
    setReplacingMeal(null);
  };

  const currentMealType = replacingMeal && weeklyPlan
    ? weeklyPlan[replacingMeal.dayIndex].meals[replacingMeal.mealIndex].mealType
    : null;
  const currentMealTitle = replacingMeal && weeklyPlan
    ? weeklyPlan[replacingMeal.dayIndex].meals[replacingMeal.mealIndex].title
    : null;

  const POOL_MAP: Record<string, Omit<WeekMeal, 'id' | 'approved'>[]> = {
    'BREAKFAST': ALL_BREAKFASTS,
    'LUNCH - MAIN': ALL_LUNCH_MAINS,
    'LUNCH - SIDE': ALL_LUNCH_SIDES,
    'DINNER - MAIN': ALL_DINNER_MAINS,
    'DINNER - SIDE': ALL_DINNER_SIDES,
  };
  const replacementOptions = currentMealType
    ? (POOL_MAP[currentMealType] || []).filter((m) => m.title !== currentMealTitle)
    : [];

  return (
    <div className="weekly-page">
      {/* Generate state */}
      {!weeklyPlan && (
        <div className="weekly-page__generate-wrap">
          <div className="weekly-page__generate-card">
            <h1 className="weekly-page__generate-title">
              Hi {user?.firstName || 'there'}! Let's plan your week 🍽️
            </h1>
            <p className="weekly-page__generate-desc">
              Generate a personalized 7-day meal plan, review it, swap meals you don't like, and approve your final selections.
            </p>
            <button
              className="weekly-page__generate-btn"
              onClick={handleGenerate}
              disabled={isGenerating}
            >
              {isGenerating ? 'Generating...' : 'Generate Weekly Meal Plan'}
            </button>
          </div>
        </div>
      )}

      {/* Weekly plan state */}
      {weeklyPlan && (
        <div className="weekly-page__plan">
          {isGenerating && (
            <div className="weekly-page__regenerating">
              <LoadingSpinner message="Generating your plan..." />
            </div>
          )}
          {!isGenerating && (
            <>
              <div className="weekly-page__plan-header">
                <h2 className="weekly-page__plan-title">Your Weekly Plan</h2>
                <button className="weekly-page__regen-btn" onClick={handleRegenerate}>
                  Regenerate Plan
                </button>
              </div>
              <div className="weekly-page__days-scroll">
                {weeklyPlan.map((day, dayIndex) => (
                  <div key={day.day} className="weekly-day-card">
                    <div className="weekly-day-card__header">
                      <span className="weekly-day-card__name">{day.day}</span>
                      <div className="weekly-day-card__header-right">
                        <span className="weekly-day-card__cals">{day.totalCalories} cal</span>
                        <button
                          className="weekly-day-card__collapse-btn"
                          onClick={() => handleToggleCollapse(dayIndex)}
                        >
                          {day.collapsed ? '+' : '−'}
                        </button>
                      </div>
                    </div>
                    {!day.collapsed && (
                      <div className="weekly-day-card__meals">
                        {day.meals.map((meal, mealIndex) => (
                          <div key={meal.id} className={`meal-item${meal.approved ? ' meal-item--approved' : ''}`}>
                            <span className="meal-item__type">{meal.mealType}</span>
                            <div
                              className="meal-item__body"
                              style={{ cursor: meal.recipeId ? 'pointer' : 'default' }}
                              onClick={() => handleOpenRecipe(meal.recipeId)}
                              title={meal.recipeId ? 'Tarif detayını gör' : undefined}
                            >
                              <img
                                src={meal.image}
                                alt={meal.title}
                                className="meal-item__img"
                              />
                              <div className="meal-item__info">
                                <span className="meal-item__title">{meal.title}</span>
                                <span className="meal-item__cals">{meal.calories} cal</span>
                              </div>
                            </div>
                            <div className="meal-item__actions">
                              <button
                                className="meal-item__replace-btn"
                                onClick={() => handleOpenReplace(dayIndex, mealIndex)}
                              >
                                Replace
                              </button>
                              <button
                                className={`meal-item__approve-btn${meal.approved ? ' meal-item__approve-btn--done' : ''}`}
                                onClick={() => handleApprove(dayIndex, mealIndex)}
                              >
                                {meal.approved ? 'Approved ✓' : 'Approve'}
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* Replacement Modal */}
      {replacingMeal !== null && (
        <div className="replacement-modal__backdrop" onClick={() => setReplacingMeal(null)}>
          <div className="replacement-modal" onClick={(e) => e.stopPropagation()}>
            <div className="replacement-modal__header">
              <h3 className="replacement-modal__title">Choose a Replacement</h3>
              <button className="replacement-modal__close" onClick={() => setReplacingMeal(null)}>
                ✕
              </button>
            </div>
            <div className="replacement-modal__list">
              {replacementOptions.length === 0 && (
                <p style={{ color: '#6b7280', padding: '1rem' }}>No alternatives available for this meal type.</p>
              )}
              {replacementOptions.map((option, idx) => (
                <div key={`${option.title}-${idx}`} className="replacement-option">
                  <img src={option.image} alt={option.title} className="replacement-option__img" />
                  <div className="replacement-option__info">
                    <span className="replacement-option__title">{option.title}</span>
                    <span className="replacement-option__meta">{option.calories} cal · {option.protein}g protein</span>
                  </div>
                  <button
                    className="replacement-option__select-btn"
                    onClick={() => handleSelectReplacement(option)}
                  >
                    Select
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Recipe Detail Modal */}
      {(recipeDetail || recipeLoading) && (
        <div className="recipe-modal-overlay" onClick={() => { setRecipeDetail(null); setRecipeLoading(false); }}>
          <div className="recipe-modal" onClick={e => e.stopPropagation()}>
            <button className="recipe-modal__close" onClick={() => { setRecipeDetail(null); setRecipeLoading(false); }}>✕</button>
            {recipeLoading && <LoadingSpinner message="Tarif yükleniyor..." />}
            {recipeDetail && (
              <>
                <h2 className="recipe-modal__title">{recipeDetail.title}</h2>
                <div className="recipe-modal__meta">
                  {recipeDetail.prepTimeMin != null && <span>🕐 Hazırlık: {recipeDetail.prepTimeMin} dk</span>}
                  {recipeDetail.cookTimeMin != null && <span>🍳 Pişirme: {recipeDetail.cookTimeMin} dk</span>}
                  {recipeDetail.servings != null && <span>🍽️ {recipeDetail.servings} porsiyon</span>}
                </div>
                <div className="recipe-modal__nutrition">
                  <span>{recipeDetail.calories} kcal</span>
                  <span>Protein: {recipeDetail.protein}g</span>
                  <span>Karbonhidrat: {recipeDetail.carbs}g</span>
                  <span>Yağ: {recipeDetail.fat}g</span>
                </div>
                {recipeDetail.ingredients && (
                  <div className="recipe-modal__section">
                    <h3>Malzemeler</h3>
                    <p style={{ whiteSpace: 'pre-line' }}>{recipeDetail.ingredients}</p>
                  </div>
                )}
                {recipeDetail.instructions && (
                  <div className="recipe-modal__section">
                    <h3>Yapılış</h3>
                    <p style={{ whiteSpace: 'pre-line' }}>{recipeDetail.instructions}</p>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
