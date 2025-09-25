<template>
  <div class="project-form">
    <h2>Alta de Proyecto</h2>
    <form @submit.prevent="submitForm">
      <div>
        <label for="name">Nombre del proyecto:</label>
        <input type="text" id="name" v-model="project.name" required />
      </div>

      <div>
        <label for="ong">ONG Originante:</label>
        <input type="text" id="ong" v-model="project.ong" required />
      </div>

      <div>
        <label for="startDate">Fecha de inicio:</label>
        <input type="date" id="startDate" v-model="project.startDate" required />
      </div>

      <div>
        <label for="endDate">Fecha de fin:</label>
        <input type="date" id="endDate" v-model="project.endDate" required />
      </div>

      <div>
        <label for="planEconomico">Plan económico:</label>
        <textarea id="planEconomico" v-model="project.planEconomico" required></textarea>
      </div>

      <div>
        <h3>Plan de trabajo / etapas</h3>
        <div v-for="(etapa, index) in project.etapas" :key="index" class="etapa">
          <input type="text" v-model="etapa.nombre" placeholder="Nombre de la etapa" required />
          <input type="date" v-model="etapa.startDate" required />
          <input type="date" v-model="etapa.endDate" required />
          <button type="button" @click="removeEtapa(index)">Eliminar</button>
        </div>
        <button type="button" @click="addEtapa">Agregar etapa</button>
      </div>

      <button type="submit">Crear Proyecto</button>
    </form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const project = reactive({
  name: '',
  ong: '',
  startDate: '',
  endDate: '',
  planEconomico: '',
  etapas: [],
})

function addEtapa() {
  project.etapas.push({ nombre: '', startDate: '', endDate: '' })
}

function removeEtapa(index) {
  project.etapas.splice(index, 1)
}

function submitForm() {
  console.log('Proyecto creado:', JSON.parse(JSON.stringify(project)))
  // Limpiar el formulario
  project.name = ''
  project.ong = ''
  project.startDate = ''
  project.endDate = ''
  project.planEconomico = ''
  project.etapas = []
}
</script>

<style scoped>
.project-form {
  max-width: 600px;
  margin: 2rem auto;
  padding: 2rem;
  border: 1px solid #ccc;
  border-radius: 8px;
}
.project-form div {
  margin-bottom: 1rem;
}
.project-form label {
  display: block;
  margin-bottom: 0.5rem;
}
.project-form input,
.project-form textarea {
  width: 100%;
  padding: 0.5rem;
  box-sizing: border-box;
}
.project-form button {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
}
.etapa {
  border: 1px solid #eee;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 4px;
}
</style>
