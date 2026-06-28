# NutriFlow Frontend - Development Setup

## Quick Start

### Prerequisites
- Node.js 16+ ([Download](https://nodejs.org/))
- npm or yarn

### Installation

```bash
# Clone or extract the project
cd BitirmeAraYuz

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm start
```

The app will open at `http://localhost:3000`

## Demo Credentials

**Email:** john@example.com  
**Password:** password123

First login will show the onboarding flow (only once).

## Project Features

- ✅ Complete authentication flow with onboarding
- ✅ Dashboard with meal suggestions
- ✅ Recipe browser with search
- ✅ Saved recipes management
- ✅ User profile management
- ✅ Responsive design
- ✅ Production-ready architecture
- ✅ Backend-ready services layer

## Available Scripts

```bash
npm start      # Start development server
npm build      # Build for production
npm test       # Run tests
npm eject      # Eject from Create React App (irreversible)
```

## Documentation

- [README.md](./README.md) - Project overview
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Architecture guide
- [API_INTEGRATION.md](./API_INTEGRATION.md) - Backend integration
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - File structure

## Key Technologies

- React 18
- React Router v6
- TypeScript
- CSS3 with CSS Variables
- Context API for state

## Folder Structure

```
src/
├── components/    # React components
├── pages/         # Page components
├── layouts/       # Layout wrappers
├── services/      # Business logic
├── hooks/         # Custom hooks
├── context/       # Global state
├── types/         # Type definitions
├── mock/          # Mock data
├── styles/        # CSS files
└── App.tsx        # Main app
```

## Development Tips

1. **Mock Data** - All services use mock data by default
2. **Hot Reload** - Changes auto-refresh without reload
3. **TypeScript** - Full type safety across the app
4. **Responsive** - Test on mobile using Chrome DevTools

## Testing the App

### Login Flow
1. Use demo credentials
2. Fill out onboarding (only first time)
3. See dashboard with meal suggestions

### Features to Try
- ✅ Search recipes
- ✅ Save/unsave recipes
- ✅ Edit profile
- ✅ Logout and login again (onboarding skipped)

## Connecting to Backend

See [API_INTEGRATION.md](./API_INTEGRATION.md) for detailed instructions on:
- Replacing mock data with API calls
- Setting up authentication
- Error handling
- Token management

## Common Commands

```bash
# Install new package
npm install package-name

# Remove package
npm uninstall package-name

# Update packages
npm update

# Check for security issues
npm audit
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Production Build

```bash
npm run build
```

This creates a `build/` folder ready for deployment:
- Optimized bundle
- Tree-shaken code
- Minified assets

## Troubleshooting

**Port 3000 already in use:**
```bash
PORT=3001 npm start
```

**Node modules issues:**
```bash
rm -rf node_modules
npm install
```

**Clear cache:**
```bash
npm cache clean --force
```

## Next Steps

1. ✅ Explore the codebase
2. ✅ Read the architecture guide
3. ✅ Connect to your backend
4. ✅ Customize styling
5. ✅ Deploy to production

---

**Happy coding! 🚀**
