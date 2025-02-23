<template>
  <div class="recommendation-container">
    <h2>🏥 Hospital Artwork Recommendation</h2>

    <!-- 🏥 Hospital Selection Fields -->
    <div class="input-section">

      <!-- 🖼️ Interior Tone -->
      <label>병원 인테리어 톤:</label>
      <select v-model="interior_tone">
        <option>화이트</option>
        <option>베이지</option>
        <option>브라운</option>
        <option>블랙</option>
      </select>

      <!-- 🏥 Hospital Department -->
      <label>병원 진료 과목:</label>
      <select v-model="department">
        <option>피부과</option>
        <option>성형외과</option>
        <option>소아과</option>
        <option>산부인과</option>
        <option>치과</option>
      </select>

      <!-- 🖼️ Canvas Installation Space -->
      <label>홀로캔버스 설치 공간:</label>
      <select v-model="installation_space">
        <option>로비</option>
        <option>대기실</option>
        <option>병실</option>
        <option>복도</option>
      </select>

      <!-- 👶 Patient Age Group -->
      <label>환자 연령대:</label>
      <select v-model="patient_age">
        <option>10대 이하</option>
        <option>20대</option>
        <option>30대</option>
        <option>40대</option>
        <option>50대</option>
        <option>60대 이상</option>
      </select>

      <!-- 🚻 Patient Gender Ratio -->
      <label>환자 성별 비중:</label>
      <select v-model="patient_gender">
        <option>남성 우세</option>
        <option>여성 우세</option>
        <option>반반</option>
      </select>

      <button @click="fetchRecommendations">🔍 Get Recommendations</button>
    </div>

    <!-- 🔄 Loading Indicator -->
    <div v-if="loading" class="loading">Loading recommendations...</div>

    <!-- 🎨 Display Recommendations -->
    <div v-if="recommendations.length > 0" class="results">
      <h3>🎨 Recommended Artworks:</h3>
      <ul>
        <li v-for="art in recommendations" :key="art.title">
          <strong>{{ art.title }}</strong> - Similarity: {{ art.similarity.toFixed(2) }}
        </li>
      </ul>
    </div>

    <!-- ⚠️ Error Message -->
    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>
  </div>
</template>


<script>
import axios from "axios";

export default {
  data() {
    return {
      interior_tone: "화이트",
      department: "피부과",
      installation_space: "로비",
      patient_age: "30대",
      patient_gender: "반반",
      recommendations: [],
      errorMessage: "",
      loading: false,
    };
  },

  methods: {
    async fetchRecommendations() {
      this.loading = true;
      this.errorMessage = "";

      try {
        const response = await axios.get("http://127.0.0.1:8000/recommend/", {
          params: {
            interior_tone: this.interior_tone,
            department: this.department,
            installation_space: this.installation_space,
            patient_age: this.patient_age,
            patient_gender: this.patient_gender,
            mood: this.mood,
            genre: this.genre,
            medium: this.medium,
            message: this.message,
          },
        });


        this.recommendations = response.data.recommendations;
      } catch (error) {
        this.errorMessage = "⚠️ Failed to fetch recommendations. Check backend!";
        console.error("Axios error:", error);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style>
.recommendation-container {
  text-align: center;
  max-width: 600px;
  margin: auto;
}

.input-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

button {
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 16px;
}

.loading {
  font-size: 18px;
  color: blue;
}

.results {
  margin-top: 20px;
}

.error {
  color: red;
  font-weight: bold;
}
</style>
