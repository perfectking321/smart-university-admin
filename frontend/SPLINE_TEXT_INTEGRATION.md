# 🎯 How to Add Text Inside Your Spline 3D Scene

Since you want the text **"Ask Your Database Anything"** to be INSIDE the Spline scene (not HTML overlay), you need to edit your Spline scene directly. Here's how:

## 📝 **Step-by-Step Instructions**

### 1. **Open Your Spline Scene**
- Go to [spline.design](https://spline.design)
- Open your scene: `https://prod.spline.design/OC9-QHrIYJURCTbx/scene.splinecode`
- Click **"Edit"** to open the Spline Editor

### 2. **Add Text Objects**
1. In the Spline editor, click the **Text tool** (T icon) in the toolbar
2. Click anywhere in your 3D scene to create a text object
3. Type: **"Ask Your Database Anything"**

### 3. **Style the Main Title**
- **Font**: Choose a modern font (Inter, Helvetica, or similar)
- **Size**: Large (around 48-60px)
- **Color**: White (#FFFFFF) or light gray (#F1F5F9)
- **Material**: Add a slight glow or emission for better visibility

### 4. **Add Subtitle Text**
1. Create another text object
2. Type: **"Smart University Admin translates your questions about students, attendance, and courses into instant SQL results—no database knowledge required."**
3. Style it:
   - **Size**: Medium (around 18-24px)
   - **Color**: Light gray (#94A3B8)
   - **Position**: Below the main title

### 5. **Position the Text in 3D Space**
- Position the text so it's clearly visible and readable
- Consider the camera angle and 3D objects in your scene
- Make sure text doesn't get obscured by other elements

### 6. **Add Interactive Elements (Optional)**
1. Create a text object for a button: **"Get Started"**
2. Add a rectangular shape behind it to create a button appearance
3. Apply a cyan/blue color (#06B6D4) to match the theme

### 7. **Set Variables for Dynamic Control**
If you want to control the text from React:

1. **Create Variables** in Spline:
   - Right-click in the scene → **Create Variable**
   - Create variables like:
     - `titleText` (String) = "Ask Your Database Anything"
     - `subtitleText` (String) = "Smart University Admin translates..."
     - `buttonVisible` (Boolean) = true

2. **Link Variables to Text Objects**:
   - Select your text object
   - In the properties panel, find **"Text"**
   - Click the chain icon next to the text field
   - Select your variable (e.g., `titleText`)

### 8. **Export the Updated Scene**
1. Click **Export** in the top-right
2. Choose **Code** → **React**
3. Copy the new scene URL (it will be different from your original)

## 🔄 **Update Your React Code**

Once you have the new scene URL, update the SplineHero component:

```tsx
// In SplineHero.tsx, update the scene URL to your new one
<Spline
  scene="https://prod.spline.design/YOUR_NEW_SCENE_ID/scene.splinecode"
  onLoad={handleLoad}
/>
```

## 🎮 **Dynamic Text Control (Advanced)**

If you set up variables in step 7, you can control them from React:

```tsx
const handleSplineLoad = (app: Application) => {
  // Change text dynamically
  app.setVariable('titleText', 'Welcome to Smart Admin');
  app.setVariable('subtitleText', 'Your database questions, answered instantly.');

  // Show/hide button based on user interaction
  app.setVariable('buttonVisible', true);
};
```

## 💡 **Tips for Better Text Integration**

1. **Lighting**: Make sure your scene lighting highlights the text properly
2. **Contrast**: Ensure text is readable against your 3D background
3. **Animation**: Consider subtle text animations (fade-in, float effects)
4. **Mobile**: Test text readability on smaller screens
5. **Performance**: Keep text objects simple to maintain good performance

## 🚀 **Next Steps**

After editing your Spline scene:

1. Update the scene URL in `SplineHero.tsx`
2. Test the new immersive experience
3. The text will now be part of the 3D scene, not HTML overlay!

Your Spline scene will be the **main immersive element** with integrated text, exactly as you wanted! 🎯